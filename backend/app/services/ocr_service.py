"""
Serviço OCR para Documentos
Processa PDFs e imagens, extrai texto e entidades (CPF, CNPJ, CAR, etc)
"""
import os
import re
import logging
from typing import Dict, List, Optional, BinaryIO
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Resultado do processamento OCR"""
    text: str
    confidence: float
    entities: Dict[str, List[str]]
    page_count: int
    processing_time: float
    metadata: Dict


class OCRService:
    """
    Serviço de OCR usando Tesseract
    
    Recursos:
    - Extração de texto de PDF e imagens
    - Detecção automática de CPF/CNPJ
    - Extração de CAR, CCIR, emails, telefones
    - Suporte a múltiplas páginas
    """
    
    # Padrões regex para entidades
    PATTERNS = {
        'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
        'cnpj': r'\b\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}\b',
        'car': r'\b[A-Z]{2}-\d{7}-[A-F0-9]{32}\b',
        'ccir': r'\bCCIR[:\s]*(\d{3}\.\d{3}\.\d{3}\.?\d{3}-?\d)\b',
        'nirf': r'\bNIRF[:\s]*(\d{3}\.\d{3}\.\d{3}\.?\d{3}-?\d)\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b',
        'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'currency': r'R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?',
        'hectare': r'\d+(?:,\d+)?\s?(?:ha|hectares?)',
        'matricula': r'\bMatrícula[:\s]*(\d{4,8})\b',
        'protocolo': r'\bProtocolo[:\s]*([A-Z0-9-]+)\b',
    }
    
    @classmethod
    async def extract_text_from_image(cls, image_bytes: bytes) -> str:
        """
        Extrai texto de uma imagem usando Tesseract
        
        Args:
            image_bytes: Bytes da imagem
            
        Returns:
            Texto extraído
        """
        try:
            import pytesseract
            from PIL import Image
            import io
            
            # Carregar imagem dos bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Converter para RGB se necessário
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Realizar OCR em português
            text = pytesseract.image_to_string(
                image,
                lang='por',
                config='--psm 6 --oem 3'
            )
            
            logger.info(f"✅ OCR: Extraídos {len(text)} caracteres da imagem")
            return text
            
        except ImportError:
            logger.error("pytesseract não instalado. Instale: pip install pytesseract")
            raise Exception("pytesseract não disponível")
        except Exception as e:
            logger.error(f"Erro no OCR da imagem: {e}")
            raise
    
    @classmethod
    async def extract_text_from_pdf(cls, pdf_bytes: bytes, use_ocr: bool = True) -> Dict:
        """
        Extrai texto de PDF (tenta nativo primeiro, depois OCR se necessário)
        
        Args:
            pdf_bytes: Bytes do PDF
            use_ocr: Se True, usa OCR em PDFs sem texto nativo
            
        Returns:
            Dict com texto extraído e metadados
        """
        import time
        start_time = time.time()
        
        try:
            import PyPDF2
            import io
            
            # Tentar extração nativa primeiro
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            page_count = len(pdf_reader.pages)
            
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            
            text = '\n\n'.join(text_parts)
            
            # Se não tem texto e OCR está habilitado, usar OCR
            if not text.strip() and use_ocr:
                logger.info("PDF sem texto nativo, usando OCR...")
                text, page_count = await cls._extract_pdf_with_ocr(pdf_bytes)
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"✅ PDF processado: {len(text)} caracteres, "
                f"{page_count} páginas, {processing_time:.2f}s"
            )
            
            return {
                'text': text,
                'page_count': page_count,
                'processing_time': processing_time,
                'method': 'native' if text.strip() else 'ocr'
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF: {e}")
            raise
    
    @classmethod
    async def _extract_pdf_with_ocr(cls, pdf_bytes: bytes) -> tuple:
        """Converte PDF em imagens e aplica OCR"""
        try:
            from pdf2image import convert_from_bytes
            import pytesseract
            
            # Converter PDF para imagens (300 DPI para boa qualidade)
            images = convert_from_bytes(pdf_bytes, dpi=300)
            page_count = len(images)
            
            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"OCR página {i+1}/{page_count}...")
                
                page_text = pytesseract.image_to_string(
                    image,
                    lang='por',
                    config='--psm 6 --oem 3'
                )
                text_parts.append(page_text)
            
            full_text = '\n\n'.join(text_parts)
            return full_text, page_count
            
        except ImportError:
            logger.error("pdf2image não instalado. Instale: pip install pdf2image")
            raise Exception("pdf2image não disponível")
        except Exception as e:
            logger.error(f"Erro no OCR do PDF: {e}")
            return "", 0
    
    @classmethod
    def extract_cpf_cnpj(cls, text: str) -> Dict[str, List[str]]:
        """
        Extrai CPF e CNPJ do texto
        
        Args:
            text: Texto para análise
            
        Returns:
            Dict com listas de CPFs e CNPJs encontrados
        """
        cpfs = re.findall(cls.PATTERNS['cpf'], text)
        cnpjs = re.findall(cls.PATTERNS['cnpj'], text)
        
        # Limpar e deduplicar
        cpfs_clean = list(set([cls._clean_document(cpf) for cpf in cpfs]))
        cnpjs_clean = list(set([cls._clean_document(cnpj) for cnpj in cnpjs]))
        
        # Validar CPFs/CNPJs básicos
        cpfs_valid = [cpf for cpf in cpfs_clean if cls._validate_cpf(cpf)]
        cnpjs_valid = [cnpj for cnpj in cnpjs_clean if cls._validate_cnpj(cnpj)]
        
        logger.info(f"Encontrados: {len(cpfs_valid)} CPFs, {len(cnpjs_valid)} CNPJs")
        
        return {
            'cpf': cpfs_valid,
            'cnpj': cnpjs_valid
        }
    
    @classmethod
    def _extract_all_entities(cls, text: str) -> Dict[str, List[str]]:
        """Extrai todas as entidades conhecidas do texto"""
        entities = {}
        
        for entity_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                # Limpar e deduplicar
                cleaned = list(set([cls._clean_value(m) for m in matches]))
                entities[entity_type] = cleaned
        
        return entities
    
    @classmethod
    async def process_document(cls, file: BinaryIO, filename: str) -> OCRResult:
        """
        Processa documento completo (PDF ou imagem)
        
        Args:
            file: Arquivo binário
            filename: Nome do arquivo
            
        Returns:
            OCRResult com texto e entidades extraídas
        """
        import time
        start_time = time.time()
        
        file_bytes = await file.read()
        
        # Determinar tipo do arquivo
        ext = os.path.splitext(filename)[1].lower()
        
        try:
            if ext == '.pdf':
                # Processar PDF
                result = await cls.extract_text_from_pdf(file_bytes, use_ocr=True)
                text = result['text']
                page_count = result['page_count']
                method = result['method']
                
            elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                # Processar imagem
                text = await cls.extract_text_from_image(file_bytes)
                page_count = 1
                method = 'ocr'
                
            else:
                raise ValueError(f"Formato não suportado: {ext}")
            
            # Extrair entidades
            entities = cls._extract_all_entities(text)
            
            # Calcular confiança
            confidence = cls._calculate_confidence(text, entities)
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"✅ Documento processado: {filename}, "
                f"{len(text)} chars, {len(entities)} tipos de entidades"
            )
            
            return OCRResult(
                text=text,
                confidence=confidence,
                entities=entities,
                page_count=page_count,
                processing_time=processing_time,
                metadata={
                    'filename': filename,
                    'file_size': len(file_bytes),
                    'method': method,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar documento {filename}: {e}")
            raise
    
    @staticmethod
    def _clean_document(doc: str) -> str:
        """Remove formatação de CPF/CNPJ"""
        return re.sub(r'[^\d]', '', doc)
    
    @staticmethod
    def _clean_value(value: str) -> str:
        """Limpa valor extraído"""
        return ' '.join(value.split()).strip()
    
    @staticmethod
    def _validate_cpf(cpf: str) -> bool:
        """Validação básica de CPF (apenas formato e dígitos)"""
        cpf_clean = re.sub(r'[^\d]', '', cpf)
        
        if len(cpf_clean) != 11:
            return False
        
        # Rejeitar CPFs com todos dígitos iguais
        if len(set(cpf_clean)) == 1:
            return False
        
        return True
    
    @staticmethod
    def _validate_cnpj(cnpj: str) -> bool:
        """Validação básica de CNPJ (apenas formato e dígitos)"""
        cnpj_clean = re.sub(r'[^\d]', '', cnpj)
        
        if len(cnpj_clean) != 14:
            return False
        
        # Rejeitar CNPJs com todos dígitos iguais
        if len(set(cnpj_clean)) == 1:
            return False
        
        return True
    
    @staticmethod
    def _calculate_confidence(text: str, entities: Dict) -> float:
        """Calcula score de confiança baseado no conteúdo"""
        if not text:
            return 0.0
        
        # Fatores de confiança
        text_length_score = min(len(text) / 1000, 0.5)
        entities_score = min(len(entities) * 0.1, 0.3)
        
        # Penalizar textos muito curtos ou muito confusos
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        
        if avg_word_length < 2 or avg_word_length > 20:
            return max(text_length_score + entities_score - 0.2, 0.1)
        
        return min(text_length_score + entities_score + 0.2, 1.0)
