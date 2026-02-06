"""
Sistema de OCR (Optical Character Recognition) para Documentos
Extrai texto de PDFs, imagens e documentos escaneados
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Resultado da extração OCR"""
    text: str
    confidence: float  # 0-1
    language: str
    page_count: int
    entities_found: Dict[str, List[str]]  # CPF, CNPJ, CAR, etc
    metadata: Dict
    processing_time: float


@dataclass
class ExtractedEntity:
    """Entidade extraída do texto"""
    type: str  # cpf, cnpj, car, email, phone, date
    value: str
    confidence: float
    position: int


class OCREngine:
    """
    Engine de OCR usando múltiplas bibliotecas
    
    Suporta:
    - PDFs (texto nativo + OCR)
    - Imagens (JPG, PNG, TIFF)
    - Documentos escaneados
    
    Detecta automaticamente:
    - CPF/CNPJ
    - CAR/CCIR
    - Emails
    - Telefones
    - Datas
    - Endereços
    """
    
    # Padrões regex para extração de entidades
    PATTERNS = {
        'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
        'cnpj': r'\b\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}\b',
        'car': r'\b[A-Z]{2}-\d{7}-[A-F0-9]{32}\b',
        'ccir': r'\bCCIR[:\s]*(\d{3}\.\d{3}\.\d{3}\.?\d{3}-?\d)\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b',
        'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'currency': r'R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?',
        'hectare': r'\d+(?:,\d+)?\s?(?:ha|hectares?)',
    }
    
    @classmethod
    async def extract_text_from_pdf(
        cls,
        file_path: str,
        use_ocr: bool = True
    ) -> OCRResult:
        """Extrai texto de PDF"""
        import time
        start_time = time.time()
        
        try:
            # Tentar extrair texto nativo primeiro (mais rápido)
            text, page_count = await cls._extract_native_pdf_text(file_path)
            
            # Se não encontrou texto e OCR está habilitado, usar OCR
            if not text.strip() and use_ocr:
                logger.info(f"PDF sem texto nativo, usando OCR: {file_path}")
                text, page_count = await cls._extract_pdf_with_ocr(file_path)
            
            # Extrair entidades
            entities_found = cls._extract_entities(text)
            
            # Calcular confiança baseada na quantidade de texto
            confidence = min(len(text) / 1000, 1.0) if text else 0.0
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"✅ OCR concluído: {len(text)} caracteres, "
                f"{page_count} páginas, {processing_time:.2f}s"
            )
            
            return OCRResult(
                text=text,
                confidence=confidence,
                language='pt-BR',
                page_count=page_count,
                entities_found=entities_found,
                metadata={
                    'file_path': file_path,
                    'file_size': os.path.getsize(file_path),
                    'method': 'native' if text else 'ocr'
                },
                processing_time=processing_time
            )
        
        except Exception as e:
            logger.error(f"Erro no OCR: {e}")
            raise
    
    @classmethod
    async def _extract_native_pdf_text(cls, file_path: str) -> Tuple[str, int]:
        """Extrai texto nativo de PDF (sem OCR)"""
        try:
            import PyPDF2
            
            text_parts = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())
            
            full_text = '\n\n'.join(text_parts)
            return full_text, page_count
        
        except Exception as e:
            logger.warning(f"Erro ao extrair texto nativo: {e}")
            return "", 0
    
    @classmethod
    async def _extract_pdf_with_ocr(cls, file_path: str) -> Tuple[str, int]:
        """Extrai texto de PDF usando OCR (para PDFs escaneados)"""
        try:
            import pytesseract
            from pdf2image import convert_from_path
            from PIL import Image
            
            # Converter PDF em imagens
            images = convert_from_path(file_path, dpi=300)
            page_count = len(images)
            
            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"Processando página {i+1}/{page_count} com OCR...")
                
                # OCR na imagem
                text = pytesseract.image_to_string(
                    image,
                    lang='por',  # Português
                    config='--psm 6'  # Assume um único bloco uniforme de texto
                )
                text_parts.append(text)
            
            full_text = '\n\n'.join(text_parts)
            return full_text, page_count
        
        except Exception as e:
            logger.error(f"Erro no OCR: {e}")
            return "", 0
    
    @classmethod
    async def extract_text_from_image(
        cls,
        file_path: str
    ) -> OCRResult:
        """Extrai texto de imagem"""
        import time
        start_time = time.time()
        
        try:
            import pytesseract
            from PIL import Image
            
            # Carregar imagem
            image = Image.open(file_path)
            
            # OCR
            text = pytesseract.image_to_string(
                image,
                lang='por',
                config='--psm 6'
            )
            
            # Extrair entidades
            entities_found = cls._extract_entities(text)
            
            # Confiança baseada no texto extraído
            confidence = min(len(text) / 500, 1.0) if text else 0.0
            
            processing_time = time.time() - start_time
            
            logger.info(
                f"✅ OCR de imagem concluído: {len(text)} caracteres, "
                f"{processing_time:.2f}s"
            )
            
            return OCRResult(
                text=text,
                confidence=confidence,
                language='pt-BR',
                page_count=1,
                entities_found=entities_found,
                metadata={
                    'file_path': file_path,
                    'file_size': os.path.getsize(file_path),
                    'image_size': image.size
                },
                processing_time=processing_time
            )
        
        except Exception as e:
            logger.error(f"Erro no OCR de imagem: {e}")
            raise
    
    @classmethod
    def _extract_entities(cls, text: str) -> Dict[str, List[str]]:
        """Extrai entidades (CPF, CNPJ, etc) do texto"""
        entities = {}
        
        for entity_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            if matches:
                # Limpar e deduplicar
                cleaned_matches = list(set([
                    cls._clean_entity(match) 
                    for match in matches
                ]))
                
                entities[entity_type] = cleaned_matches
        
        return entities
    
    @staticmethod
    def _clean_entity(value: str) -> str:
        """Limpa valor extraído"""
        # Remover espaços extras
        value = ' '.join(value.split())
        # Remover pontuação extra no final
        value = value.rstrip('.,;:')
        return value
    
    @classmethod
    async def process_document_batch(
        cls,
        file_paths: List[str],
        use_ocr: bool = True
    ) -> List[OCRResult]:
        """Processa múltiplos documentos em lote"""
        results = []
        
        for file_path in file_paths:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.pdf':
                    result = await cls.extract_text_from_pdf(file_path, use_ocr)
                elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                    result = await cls.extract_text_from_image(file_path)
                else:
                    logger.warning(f"Formato não suportado: {ext}")
                    continue
                
                results.append(result)
            
            except Exception as e:
                logger.error(f"Erro ao processar {file_path}: {e}")
                continue
        
        return results
    
    @classmethod
    async def search_text_in_document(
        cls,
        file_path: str,
        search_terms: List[str]
    ) -> Dict[str, List[int]]:
        """Busca termos específicos no documento e retorna páginas"""
        
        result = await cls.extract_text_from_pdf(file_path)
        text = result.text.lower()
        
        findings = {}
        for term in search_terms:
            term_lower = term.lower()
            
            # Contar ocorrências
            count = text.count(term_lower)
            
            if count > 0:
                # Encontrar posições
                positions = []
                start = 0
                while True:
                    pos = text.find(term_lower, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1
                
                findings[term] = {
                    'count': count,
                    'positions': positions[:10]  # Primeiras 10
                }
        
        return findings
    
    @classmethod
    def extract_tables(cls, text: str) -> List[List[str]]:
        """Extrai tabelas do texto (heurística simples)"""
        tables = []
        
        lines = text.split('\n')
        current_table = []
        
        for line in lines:
            # Detectar linhas tabulares (múltiplos espaços ou tabs)
            if re.search(r'\s{3,}|\t', line):
                cells = re.split(r'\s{3,}|\t', line.strip())
                current_table.append(cells)
            else:
                if len(current_table) >= 3:  # Mínimo 3 linhas para ser tabela
                    tables.append(current_table)
                current_table = []
        
        # Adicionar última tabela se existir
        if len(current_table) >= 3:
            tables.append(current_table)
        
        return tables
    
    @classmethod
    async def extract_and_validate_documents(
        cls,
        file_path: str,
        expected_entities: Dict[str, str]
    ) -> Dict[str, bool]:
        """
        Extrai e valida se documento contém entidades esperadas
        
        Args:
            file_path: Caminho do arquivo
            expected_entities: Dict com entidades esperadas, ex:
                {'cpf': '123.456.789-00', 'car': 'SP-1234567-...'}
        
        Returns:
            Dict indicando se cada entidade foi encontrada
        """
        result = await cls.extract_text_from_pdf(file_path)
        
        validation = {}
        for entity_type, expected_value in expected_entities.items():
            found_entities = result.entities_found.get(entity_type, [])
            
            # Normalizar para comparação
            expected_normalized = re.sub(r'[^\w]', '', expected_value)
            found_normalized = [
                re.sub(r'[^\w]', '', found)
                for found in found_entities
            ]
            
            validation[entity_type] = expected_normalized in found_normalized
        
        return validation
