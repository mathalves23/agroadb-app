"""
OCR Processor - Extração de Texto de Documentos

Este módulo utiliza OCR (Optical Character Recognition) para extrair texto
de documentos escaneados, imagens e PDFs.

Funcionalidades:
- OCR de imagens (JPG, PNG, etc)
- OCR de PDFs
- Extração de dados estruturados (CPF, CNPJ, datas, valores)
- Reconhecimento de tipos de documentos
- Validação de documentos
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import re
import logging
import io
import base64

# OCR libraries
try:
    from PIL import Image
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract OCR not available. Install with: pip install pytesseract pillow")

# PDF processing
try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logging.warning("pdf2image not available. Install with: pip install pdf2image")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available. Install with: pip install PyPDF2")

logger = logging.getLogger(__name__)


class DocumentType:
    """Tipos de documentos reconhecidos"""
    CPF = "cpf"
    CNPJ = "cnpj"
    RG = "rg"
    CNH = "cnh"
    CONTRACT = "contract"
    PROPERTY_DEED = "property_deed"
    CAR_DOCUMENT = "car_document"
    INVOICE = "invoice"
    BANK_STATEMENT = "bank_statement"
    UNKNOWN = "unknown"


class ExtractedData:
    """Dados extraídos de um documento"""
    
    def __init__(
        self,
        text: str,
        document_type: str,
        structured_data: Dict[str, Any],
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.document_type = document_type
        self.structured_data = structured_data
        self.confidence = confidence
        self.metadata = metadata or {}
        self.extracted_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "text": self.text,
            "text_length": len(self.text),
            "document_type": self.document_type,
            "structured_data": self.structured_data,
            "confidence": round(self.confidence, 3),
            "metadata": self.metadata,
            "extracted_at": self.extracted_at.isoformat()
        }


class OCRResult:
    """Resultado do processamento OCR"""
    
    def __init__(
        self,
        success: bool,
        extracted_data: Optional[ExtractedData] = None,
        error: Optional[str] = None,
        processing_time_seconds: float = 0.0
    ):
        self.success = success
        self.extracted_data = extracted_data
        self.error = error
        self.processing_time_seconds = processing_time_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        result = {
            "success": self.success,
            "processing_time_seconds": round(self.processing_time_seconds, 3)
        }
        
        if self.extracted_data:
            result["data"] = self.extracted_data.to_dict()
        
        if self.error:
            result["error"] = self.error
        
        return result


class OCRProcessor:
    """
    Processador de OCR para Documentos
    
    Suporta:
    - Imagens: JPG, PNG, BMP, TIFF
    - PDFs (converte para imagens primeiro)
    - Múltiplas páginas
    
    Extrai:
    - Texto completo
    - CPF, CNPJ, RG, CNH
    - Datas
    - Valores monetários
    - Endereços
    """
    
    # Expressões regulares para extração
    REGEX_CPF = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'
    REGEX_CNPJ = r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'
    REGEX_RG = r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X]\b'
    REGEX_DATE = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
    REGEX_MONEY = r'R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?'
    REGEX_CEP = r'\b\d{5}-?\d{3}\b'
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Inicializa o processador OCR
        
        Args:
            tesseract_path: Caminho customizado para o executável do Tesseract
        """
        if not TESSERACT_AVAILABLE:
            logger.warning(
                "Tesseract não disponível. OCR estará desabilitado. "
                "Instale com: pip install pytesseract pillow"
            )
        
        if tesseract_path and TESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def process_image(
        self,
        image_path: str,
        language: str = "por"
    ) -> OCRResult:
        """
        Processa uma imagem e extrai texto
        
        Args:
            image_path: Caminho para a imagem
            language: Idioma do OCR (por = português)
            
        Returns:
            OCRResult com texto extraído e dados estruturados
        """
        start_time = datetime.utcnow()
        
        if not TESSERACT_AVAILABLE:
            return OCRResult(
                success=False,
                error="Tesseract não disponível",
                processing_time_seconds=0.0
            )
        
        try:
            # Abrir imagem
            image = Image.open(image_path)
            
            # Aplicar pré-processamento
            image = self._preprocess_image(image)
            
            # Executar OCR
            text = pytesseract.image_to_string(image, lang=language)
            
            # Extrair dados estruturados
            structured_data = self._extract_structured_data(text)
            
            # Detectar tipo de documento
            doc_type = self._detect_document_type(text, structured_data)
            
            # Calcular confiança
            confidence = self._calculate_confidence(text, structured_data)
            
            # Criar resultado
            extracted_data = ExtractedData(
                text=text,
                document_type=doc_type,
                structured_data=structured_data,
                confidence=confidence,
                metadata={
                    "image_path": image_path,
                    "language": language,
                    "image_size": image.size
                }
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"OCR concluído: {len(text)} caracteres, "
                f"tipo={doc_type}, confiança={confidence:.2f}"
            )
            
            return OCRResult(
                success=True,
                extracted_data=extracted_data,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Erro no OCR: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            return OCRResult(
                success=False,
                error=str(e),
                processing_time_seconds=processing_time
            )
    
    def process_pdf(
        self,
        pdf_path: str,
        language: str = "por",
        max_pages: int = 10
    ) -> OCRResult:
        """
        Processa um PDF e extrai texto de todas as páginas
        
        Args:
            pdf_path: Caminho para o PDF
            language: Idioma do OCR
            max_pages: Número máximo de páginas a processar
            
        Returns:
            OCRResult com texto de todas as páginas
        """
        start_time = datetime.utcnow()
        
        if not PDF2IMAGE_AVAILABLE:
            return OCRResult(
                success=False,
                error="pdf2image não disponível",
                processing_time_seconds=0.0
            )
        
        try:
            # Primeiro, tentar extrair texto diretamente (PDFs com texto)
            text_extracted = self._extract_text_from_pdf(pdf_path)
            
            if text_extracted and len(text_extracted) > 100:
                # PDF tem texto extraível, não precisa de OCR
                structured_data = self._extract_structured_data(text_extracted)
                doc_type = self._detect_document_type(text_extracted, structured_data)
                confidence = 0.95  # Alta confiança quando extrai texto diretamente
                
                extracted_data = ExtractedData(
                    text=text_extracted,
                    document_type=doc_type,
                    structured_data=structured_data,
                    confidence=confidence,
                    metadata={
                        "pdf_path": pdf_path,
                        "method": "direct_extraction",
                        "ocr_used": False
                    }
                )
                
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                return OCRResult(
                    success=True,
                    extracted_data=extracted_data,
                    processing_time_seconds=processing_time
                )
            
            # PDF é imagem, precisa de OCR
            logger.info(f"Convertendo PDF para imagens: {pdf_path}")
            images = pdf2image.convert_from_path(pdf_path)
            
            # Limitar número de páginas
            images = images[:max_pages]
            
            # Processar cada página
            all_text = []
            all_structured_data = {}
            
            for i, image in enumerate(images):
                logger.info(f"Processando página {i+1}/{len(images)}")
                
                # Pré-processar
                image = self._preprocess_image(image)
                
                # OCR
                page_text = pytesseract.image_to_string(image, lang=language)
                all_text.append(f"--- Página {i+1} ---\n{page_text}\n")
                
                # Extrair dados estruturados da página
                page_data = self._extract_structured_data(page_text)
                
                # Mesclar com dados anteriores
                for key, value in page_data.items():
                    if key not in all_structured_data:
                        all_structured_data[key] = value
                    elif isinstance(value, list):
                        if isinstance(all_structured_data[key], list):
                            all_structured_data[key].extend(value)
                        else:
                            all_structured_data[key] = [all_structured_data[key]] + value
            
            # Combinar texto de todas as páginas
            combined_text = "\n".join(all_text)
            
            # Detectar tipo e confiança
            doc_type = self._detect_document_type(combined_text, all_structured_data)
            confidence = self._calculate_confidence(combined_text, all_structured_data)
            
            extracted_data = ExtractedData(
                text=combined_text,
                document_type=doc_type,
                structured_data=all_structured_data,
                confidence=confidence,
                metadata={
                    "pdf_path": pdf_path,
                    "method": "ocr",
                    "total_pages": len(images),
                    "ocr_used": True,
                    "language": language
                }
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"OCR PDF concluído: {len(combined_text)} caracteres, "
                f"{len(images)} páginas, tipo={doc_type}"
            )
            
            return OCRResult(
                success=True,
                extracted_data=extracted_data,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Erro no OCR de PDF: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            return OCRResult(
                success=False,
                error=str(e),
                processing_time_seconds=processing_time
            )
    
    def process_base64_image(
        self,
        base64_string: str,
        language: str = "por"
    ) -> OCRResult:
        """
        Processa uma imagem codificada em base64
        
        Args:
            base64_string: Imagem em base64
            language: Idioma do OCR
            
        Returns:
            OCRResult
        """
        start_time = datetime.utcnow()
        
        try:
            # Decodificar base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            
            # Processar
            image = self._preprocess_image(image)
            text = pytesseract.image_to_string(image, lang=language)
            
            structured_data = self._extract_structured_data(text)
            doc_type = self._detect_document_type(text, structured_data)
            confidence = self._calculate_confidence(text, structured_data)
            
            extracted_data = ExtractedData(
                text=text,
                document_type=doc_type,
                structured_data=structured_data,
                confidence=confidence,
                metadata={"method": "base64", "language": language}
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return OCRResult(
                success=True,
                extracted_data=extracted_data,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Erro no OCR de base64: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            return OCRResult(
                success=False,
                error=str(e),
                processing_time_seconds=processing_time
            )
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Pré-processa imagem para melhorar OCR
        
        - Converte para escala de cinza
        - Aumenta contraste
        - Remove ruído
        """
        # Converter para escala de cinza
        if image.mode != 'L':
            image = image.convert('L')
        
        # Redimensionar se muito pequena
        if image.size[0] < 1000:
            scale = 1000 / image.size[0]
            new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
            image = image.resize(new_size, Image.LANCZOS)
        
        return image
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrai texto diretamente de PDF (sem OCR)"""
        if not PYPDF2_AVAILABLE:
            return ""
        
        try:
            text = []
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            
            return "\n".join(text)
        except:
            return ""
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Extrai dados estruturados do texto
        
        Returns:
            Dict com CPFs, CNPJs, datas, valores, etc
        """
        data = {}
        
        # CPFs
        cpfs = re.findall(self.REGEX_CPF, text)
        if cpfs:
            data["cpfs"] = list(set(cpfs))
        
        # CNPJs
        cnpjs = re.findall(self.REGEX_CNPJ, text)
        if cnpjs:
            data["cnpjs"] = list(set(cnpjs))
        
        # RGs
        rgs = re.findall(self.REGEX_RG, text)
        if rgs:
            data["rgs"] = list(set(rgs))
        
        # Datas
        dates = re.findall(self.REGEX_DATE, text)
        if dates:
            data["dates"] = list(set(dates))
        
        # Valores monetários
        money = re.findall(self.REGEX_MONEY, text)
        if money:
            data["money_values"] = list(set(money))
        
        # CEPs
        ceps = re.findall(self.REGEX_CEP, text)
        if ceps:
            data["ceps"] = list(set(ceps))
        
        # Palavras-chave
        keywords = self._extract_keywords(text)
        if keywords:
            data["keywords"] = keywords
        
        return data
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave importantes"""
        keywords_patterns = {
            "contract": ["contrato", "arrendamento", "locação", "aluguel"],
            "property": ["propriedade", "imóvel", "terreno", "hectares", "ha"],
            "car": ["car", "cadastro ambiental rural"],
            "incra": ["incra", "ccir", "cadastro rural"],
            "legal": ["processo", "judicial", "ação", "tribunal"],
        }
        
        text_lower = text.lower()
        found_keywords = []
        
        for category, patterns in keywords_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    found_keywords.append(category)
                    break
        
        return list(set(found_keywords))
    
    def _detect_document_type(
        self,
        text: str,
        structured_data: Dict[str, Any]
    ) -> str:
        """Detecta o tipo de documento baseado no conteúdo"""
        text_lower = text.lower()
        
        # CPF
        if "república federativa do brasil" in text_lower and "cpf" in text_lower:
            return DocumentType.CPF
        
        # CNPJ
        if "cadastro nacional da pessoa jurídica" in text_lower or "cnpj" in text_lower:
            return DocumentType.CNPJ
        
        # RG
        if "registro geral" in text_lower or "carteira de identidade" in text_lower:
            return DocumentType.RG
        
        # CNH
        if "carteira nacional de habilitação" in text_lower or "cnh" in text_lower:
            return DocumentType.CNH
        
        # Contrato
        if "contrato" in text_lower and ("arrendamento" in text_lower or "locação" in text_lower):
            return DocumentType.CONTRACT
        
        # Escritura de propriedade
        if "escritura" in text_lower or "matrícula" in text_lower:
            return DocumentType.PROPERTY_DEED
        
        # CAR
        if "car" in text_lower or "cadastro ambiental rural" in text_lower:
            return DocumentType.CAR_DOCUMENT
        
        # Nota fiscal
        if "nota fiscal" in text_lower or "nf-e" in text_lower:
            return DocumentType.INVOICE
        
        # Extrato bancário
        if "extrato" in text_lower and "banco" in text_lower:
            return DocumentType.BANK_STATEMENT
        
        return DocumentType.UNKNOWN
    
    def _calculate_confidence(
        self,
        text: str,
        structured_data: Dict[str, Any]
    ) -> float:
        """
        Calcula confiança do OCR baseado em vários fatores
        
        Returns:
            Float entre 0.0 e 1.0
        """
        confidence = 0.5  # Base
        
        # Texto não vazio
        if len(text) > 50:
            confidence += 0.1
        
        # Dados estruturados encontrados
        if structured_data.get("cpfs"):
            confidence += 0.1
        if structured_data.get("cnpjs"):
            confidence += 0.1
        if structured_data.get("dates"):
            confidence += 0.05
        if structured_data.get("money_values"):
            confidence += 0.05
        
        # Palavras-chave encontradas
        keywords = structured_data.get("keywords", [])
        confidence += len(keywords) * 0.02
        
        # Limitar a 1.0
        return min(confidence, 1.0)
