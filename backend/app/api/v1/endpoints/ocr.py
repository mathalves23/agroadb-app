"""
Endpoints para OCR de Documentos
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.domain.user import User
from app.services.ocr_service import OCRService
from app.core.audit import AuditLogger

logger = logging.getLogger(__name__)
audit_logger = AuditLogger()

router = APIRouter(prefix="/ocr", tags=["ocr"])


class OCRResponse(BaseModel):
    """Resposta do processamento OCR"""
    text: str
    confidence: float
    entities: Dict[str, List[str]]
    page_count: int
    processing_time: float
    metadata: Dict


class EntityExtractionResponse(BaseModel):
    """Resposta de extração de entidades"""
    cpf: List[str]
    cnpj: List[str]
    total_found: int


@router.post(
    "/process",
    response_model=OCRResponse,
    summary="Processa documento com OCR"
)
async def process_document_ocr(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Processa documento (PDF ou imagem) com OCR
    
    - Extrai texto
    - Detecta entidades (CPF, CNPJ, CAR, etc)
    - Retorna resultado estruturado
    
    Formatos aceitos:
    - PDF
    - Imagens: JPG, JPEG, PNG, TIFF, BMP
    """
    try:
        # Validar tipo do arquivo
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        file_ext = None
        
        if file.filename:
            import os
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Formato não suportado. Use: {', '.join(allowed_extensions)}"
                )
        
        # Validar tamanho (máx 50MB)
        file.file.seek(0, 2)  # Ir para o fim
        file_size = file.file.tell()
        file.file.seek(0)  # Voltar ao início
        
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Arquivo muito grande. Máximo: {max_size / 1024 / 1024}MB"
            )
        
        logger.info(
            f"Processando documento OCR: {file.filename} "
            f"({file_size / 1024:.1f}KB) para usuário {current_user.email}"
        )
        
        # Processar documento
        result = await OCRService.process_document(file.file, file.filename)
        
        # Log de auditoria
        await audit_logger.log(
            user_id=current_user.id,
            action="ocr_process",
            resource_type="document",
            resource_id=file.filename,
            details={
                'filename': file.filename,
                'file_size': file_size,
                'page_count': result.page_count,
                'entities_found': len(result.entities),
                'processing_time': result.processing_time
            },
            db=db
        )
        
        return OCRResponse(
            text=result.text,
            confidence=result.confidence,
            entities=result.entities,
            page_count=result.page_count,
            processing_time=result.processing_time,
            metadata=result.metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar documento OCR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar documento: {str(e)}"
        )


@router.post(
    "/extract-entities",
    response_model=EntityExtractionResponse,
    summary="Extrai CPF/CNPJ de texto"
)
async def extract_entities_from_text(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Extrai CPF e CNPJ de texto fornecido
    
    Útil quando você já tem o texto e quer apenas extrair documentos.
    """
    try:
        logger.info(f"Extraindo entidades de texto ({len(text)} chars)")
        
        # Extrair CPF/CNPJ
        entities = OCRService.extract_cpf_cnpj(text)
        
        total = len(entities.get('cpf', [])) + len(entities.get('cnpj', []))
        
        return EntityExtractionResponse(
            cpf=entities.get('cpf', []),
            cnpj=entities.get('cnpj', []),
            total_found=total
        )
    
    except Exception as e:
        logger.error(f"Erro ao extrair entidades: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao extrair entidades: {str(e)}"
        )


@router.post(
    "/extract-from-image",
    summary="Extrai texto de imagem"
)
async def extract_text_from_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Extrai apenas texto de uma imagem
    
    Mais rápido que /process quando você não precisa de análise de entidades.
    """
    try:
        # Validar formato
        import os
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato não suportado. Use imagens: JPG, PNG, TIFF, BMP"
            )
        
        # Ler bytes
        image_bytes = await file.read()
        
        # Extrair texto
        text = await OCRService.extract_text_from_image(image_bytes)
        
        return {
            'text': text,
            'length': len(text),
            'filename': file.filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao extrair texto de imagem: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao extrair texto: {str(e)}"
        )


@router.get(
    "/health",
    summary="Verifica disponibilidade do OCR"
)
async def ocr_health_check(current_user: User = Depends(get_current_user)):
    """
    Verifica se o serviço de OCR está disponível
    
    Retorna informações sobre dependências instaladas.
    """
    try:
        # Verificar dependências
        dependencies = {}
        
        try:
            import pytesseract
            dependencies['pytesseract'] = True
            
            # Tentar obter versão do Tesseract
            try:
                version = pytesseract.get_tesseract_version()
                dependencies['tesseract_version'] = str(version)
            except:
                dependencies['tesseract_version'] = 'unknown'
        except ImportError:
            dependencies['pytesseract'] = False
        
        try:
            import PIL
            dependencies['pillow'] = True
        except ImportError:
            dependencies['pillow'] = False
        
        try:
            import PyPDF2
            dependencies['pypdf2'] = True
        except ImportError:
            dependencies['pypdf2'] = False
        
        try:
            import pdf2image
            dependencies['pdf2image'] = True
        except ImportError:
            dependencies['pdf2image'] = False
        
        # Verificar se está tudo OK
        all_ok = all([
            dependencies.get('pytesseract'),
            dependencies.get('pillow'),
            dependencies.get('pypdf2')
        ])
        
        status_msg = "OK" if all_ok else "INCOMPLETE"
        
        return {
            'status': status_msg,
            'dependencies': dependencies,
            'message': 'OCR service is ready' if all_ok else 'Some dependencies missing'
        }
    
    except Exception as e:
        logger.error(f"Erro ao verificar health do OCR: {e}")
        return {
            'status': 'ERROR',
            'message': str(e)
        }
