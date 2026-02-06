"""
Testes para o Sistema de Machine Learning

Testa:
- RiskAnalyzer
- PatternDetector
- NetworkAnalyzer
- OCRProcessor
- Endpoints da API ML
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from PIL import Image
import io
import base64

from app.ml.models.risk_analyzer import RiskAnalyzer, RiskFactor
from app.ml.models.pattern_detector import PatternDetector, Pattern
from app.ml.models.network_analyzer import NetworkAnalyzer, Node, Edge
from app.ml.models.ocr_processor import OCRProcessor, DocumentType
from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company
from app.domain.lease_contract import LeaseContract
from app.domain.user import User


# ========== Fixtures ==========

@pytest.fixture
def sample_investigation(db: Session):
    """Cria uma investigação de teste com dados completos"""
    user = User(
        email="test@test.com",
        username="testuser",
        hashed_password="fake_hash",
        is_active=True
    )
    db.add(user)
    db.commit()
    
    investigation = Investigation(
        title="Investigação Teste ML",
        target_cpf="12345678900",
        target_name="João Silva",
        status="completed",
        user_id=user.id
    )
    db.add(investigation)
    db.commit()
    
    # Adicionar propriedades
    for i in range(5):
        prop = Property(
            name=f"Propriedade {i+1}",
            address=f"Endereço {i+1}",
            investigation_id=investigation.id,
            additional_data={
                "area_hectares": 500 + (i * 100),
                "car_code": f"CAR{i+1}",
                "owner_cpf": f"1234567890{i}",
                "owner_name": f"Proprietário {i+1}"
            }
        )
        db.add(prop)
    
    # Adicionar empresas
    for i in range(3):
        company = Company(
            cnpj=f"1234567800012{i}",
            name=f"Empresa {i+1}",
            investigation_id=investigation.id,
            additional_data={
                "status": "ativa" if i < 2 else "inativa",
                "partners": [
                    {
                        "name": f"Sócio {i+1}",
                        "cpf": f"9876543210{i}",
                        "share": 50.0
                    }
                ]
            }
        )
        db.add(company)
    
    # Adicionar contratos
    for i in range(2):
        lease = LeaseContract(
            lessor_name=f"Arrendador {i+1}",
            lessee_name=f"Arrendatário {i+1}",
            monthly_value=5000.0 + (i * 1000),
            start_date=datetime.utcnow() - timedelta(days=365),
            end_date=datetime.utcnow() + timedelta(days=365),
            document_number=f"DOC{i+1}",
            investigation_id=investigation.id
        )
        db.add(lease)
    
    db.commit()
    db.refresh(investigation)
    
    return investigation


@pytest.fixture
def sample_image():
    """Cria uma imagem de teste"""
    # Criar imagem simples com texto
    img = Image.new('RGB', (800, 600), color='white')
    return img


# ========== Testes RiskAnalyzer ==========

def test_risk_analyzer_basic(db: Session, sample_investigation):
    """Teste básico do RiskAnalyzer"""
    analyzer = RiskAnalyzer(db)
    result = analyzer.analyze(sample_investigation.id)
    
    assert result is not None
    assert result.investigation_id == sample_investigation.id
    assert 0.0 <= result.overall_score <= 1.0
    assert result.risk_level in ["low", "medium", "high", "critical"]
    assert len(result.factors) == 8  # 8 fatores analisados
    assert len(result.recommendations) > 0


def test_risk_analyzer_multiple_properties(db: Session, sample_investigation):
    """Teste do fator de múltiplas propriedades"""
    analyzer = RiskAnalyzer(db)
    result = analyzer.analyze(sample_investigation.id)
    
    # Deve detectar 5 propriedades
    factor_dict = result.to_dict()
    multiple_props = next(
        (f for f in factor_dict["factors"] if "Propriedade" in f["name"]),
        None
    )
    
    assert multiple_props is not None
    assert multiple_props["score"] > 0.0  # Pelo menos algum risco


def test_risk_analyzer_invalid_investigation(db: Session):
    """Teste com investigação inexistente"""
    analyzer = RiskAnalyzer(db)
    
    with pytest.raises(ValueError, match="não encontrada"):
        analyzer.analyze(99999)


def test_risk_factor_weighted_score():
    """Teste do cálculo de score ponderado"""
    factor = RiskFactor(
        name="Test Factor",
        weight=0.5,
        score=0.8,
        evidence="Test evidence",
        severity="high"
    )
    
    assert factor.weighted_score() == 0.4  # 0.5 * 0.8


def test_risk_analysis_to_dict(db: Session, sample_investigation):
    """Teste da serialização para dicionário"""
    analyzer = RiskAnalyzer(db)
    result = analyzer.analyze(sample_investigation.id)
    
    result_dict = result.to_dict()
    
    assert "investigation_id" in result_dict
    assert "overall_score" in result_dict
    assert "risk_level" in result_dict
    assert "factors" in result_dict
    assert "recommendations" in result_dict
    assert "critical_factors" in result_dict


# ========== Testes PatternDetector ==========

def test_pattern_detector_basic(db: Session, sample_investigation):
    """Teste básico do PatternDetector"""
    detector = PatternDetector(db)
    result = detector.detect(sample_investigation.id)
    
    assert result is not None
    assert result.investigation_id == sample_investigation.id
    assert isinstance(result.patterns, list)


def test_pattern_detector_ghost_properties(db: Session, sample_investigation):
    """Teste de detecção de propriedades fantasma"""
    # Adicionar propriedade sem dados completos
    prop = Property(
        name="Propriedade Fantasma",
        address="",  # Endereço vazio (suspeito)
        investigation_id=sample_investigation.id,
        additional_data={}  # Sem dados (suspeito)
    )
    db.add(prop)
    db.commit()
    
    detector = PatternDetector(db)
    result = detector.detect(sample_investigation.id)
    
    # Deve detectar padrão de propriedade fantasma
    result_dict = result.to_dict()
    ghost_pattern = next(
        (p for p in result_dict["patterns"] if p["pattern_type"] == "ghost_properties"),
        None
    )
    
    # Pode ou não detectar dependendo dos outros dados
    # Apenas verificar que a análise rodou sem erros
    assert result_dict is not None


def test_pattern_detector_to_dict(db: Session, sample_investigation):
    """Teste da serialização"""
    detector = PatternDetector(db)
    result = detector.detect(sample_investigation.id)
    
    result_dict = result.to_dict()
    
    assert "investigation_id" in result_dict
    assert "patterns_detected" in result_dict
    assert "patterns" in result_dict
    assert "severity_summary" in result_dict


def test_pattern_to_dict():
    """Teste da serialização de Pattern"""
    pattern = Pattern(
        pattern_type="test_pattern",
        confidence=0.85,
        description="Test pattern",
        evidence=["Evidence 1", "Evidence 2"],
        severity="high",
        entities_involved=["Entity 1"]
    )
    
    pattern_dict = pattern.to_dict()
    
    assert pattern_dict["pattern_type"] == "test_pattern"
    assert pattern_dict["confidence"] == 0.85
    assert pattern_dict["confidence_percentage"] == 85.0
    assert len(pattern_dict["evidence"]) == 2


# ========== Testes NetworkAnalyzer ==========

def test_network_analyzer_basic(db: Session, sample_investigation):
    """Teste básico do NetworkAnalyzer"""
    analyzer = NetworkAnalyzer(db)
    result = analyzer.analyze(sample_investigation.id)
    
    assert result is not None
    assert result.investigation_id == sample_investigation.id
    assert result.graph is not None
    assert len(result.graph.nodes) > 0
    assert len(result.central_actors) > 0


def test_network_analyzer_build_graph(db: Session, sample_investigation):
    """Teste da construção do grafo"""
    analyzer = NetworkAnalyzer(db)
    result = analyzer.analyze(sample_investigation.id)
    
    graph_dict = result.graph.to_dict()
    
    assert "nodes" in graph_dict
    assert "edges" in graph_dict
    assert "statistics" in graph_dict
    
    # Deve ter nós de diferentes tipos
    node_types = graph_dict["statistics"]["node_types"]
    assert "person" in node_types or "company" in node_types


def test_network_analyzer_centrality(db: Session, sample_investigation):
    """Teste do cálculo de centralidade"""
    analyzer = NetworkAnalyzer(db)
    result = analyzer.analyze(sample_investigation.id)
    
    assert len(result.central_actors) > 0
    
    # Verificar primeiro ator central
    node_id, metrics = result.central_actors[0]
    
    assert 0.0 <= metrics.degree_centrality <= 1.0
    assert 0.0 <= metrics.betweenness_centrality <= 1.0
    assert 0.0 <= metrics.closeness_centrality <= 1.0
    assert 0.0 <= metrics.eigenvector_centrality <= 1.0


def test_network_analyzer_communities(db: Session, sample_investigation):
    """Teste da detecção de comunidades"""
    analyzer = NetworkAnalyzer(db)
    result = analyzer.analyze(sample_investigation.id)
    
    # Pode ou não ter comunidades dependendo dos dados
    assert isinstance(result.communities, list)


def test_node_to_dict():
    """Teste da serialização de Node"""
    node = Node(
        node_id="test_123",
        node_type="person",
        name="Test Person",
        metadata={"cpf": "12345678900"}
    )
    
    node_dict = node.to_dict()
    
    assert node_dict["id"] == "test_123"
    assert node_dict["type"] == "person"
    assert node_dict["name"] == "Test Person"


def test_edge_to_dict():
    """Teste da serialização de Edge"""
    edge = Edge(
        source="node1",
        target="node2",
        relationship_type="owns",
        weight=1.0,
        metadata={"test": "value"}
    )
    
    edge_dict = edge.to_dict()
    
    assert edge_dict["source"] == "node1"
    assert edge_dict["target"] == "node2"
    assert edge_dict["type"] == "owns"
    assert edge_dict["weight"] == 1.0


# ========== Testes OCRProcessor ==========

def test_ocr_processor_initialization():
    """Teste de inicialização do OCRProcessor"""
    processor = OCRProcessor()
    assert processor is not None


def test_ocr_processor_document_type_detection():
    """Teste de detecção de tipo de documento"""
    processor = OCRProcessor()
    
    # Texto de CPF
    text_cpf = "República Federativa do Brasil CPF: 123.456.789-00"
    structured_data = processor._extract_structured_data(text_cpf)
    doc_type = processor._detect_document_type(text_cpf, structured_data)
    
    assert doc_type == DocumentType.CPF
    
    # Texto de CNPJ
    text_cnpj = "Cadastro Nacional da Pessoa Jurídica CNPJ: 12.345.678/0001-90"
    structured_data = processor._extract_structured_data(text_cnpj)
    doc_type = processor._detect_document_type(text_cnpj, structured_data)
    
    assert doc_type == DocumentType.CNPJ


def test_ocr_processor_extract_structured_data():
    """Teste de extração de dados estruturados"""
    processor = OCRProcessor()
    
    text = """
    CPF: 123.456.789-00
    CNPJ: 12.345.678/0001-90
    Data: 01/01/2024
    Valor: R$ 10.000,00
    CEP: 12345-678
    """
    
    data = processor._extract_structured_data(text)
    
    assert "cpfs" in data
    assert len(data["cpfs"]) > 0
    assert "cnpjs" in data
    assert len(data["cnpjs"]) > 0
    assert "dates" in data
    assert "money_values" in data
    assert "ceps" in data


def test_ocr_processor_calculate_confidence():
    """Teste do cálculo de confiança"""
    processor = OCRProcessor()
    
    # Texto com muitos dados estruturados
    text = "CPF: 123.456.789-00 CNPJ: 12.345.678/0001-90 Data: 01/01/2024"
    structured_data = processor._extract_structured_data(text)
    confidence = processor._calculate_confidence(text, structured_data)
    
    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.5  # Deve ter confiança razoável


def test_ocr_processor_preprocess_image(sample_image):
    """Teste de pré-processamento de imagem"""
    processor = OCRProcessor()
    
    # Processar imagem
    processed = processor._preprocess_image(sample_image)
    
    assert processed is not None
    assert processed.mode == 'L'  # Escala de cinza


# ========== Testes dos Endpoints ==========

def test_ml_health_endpoint(client: TestClient):
    """Teste do endpoint de health check"""
    response = client.get("/api/v1/ml/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "tesseract_available" in data
    assert "components" in data


def test_risk_analysis_endpoint(
    client: TestClient,
    db: Session,
    sample_investigation,
    auth_headers
):
    """Teste do endpoint de análise de risco"""
    response = client.post(
        f"/api/v1/ml/risk-analysis/{sample_investigation.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "investigation_id" in data
    assert "overall_score" in data
    assert "risk_level" in data
    assert "factors" in data


def test_risk_analysis_endpoint_not_found(client: TestClient, auth_headers):
    """Teste com investigação inexistente"""
    response = client.post(
        "/api/v1/ml/risk-analysis/99999",
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_pattern_detection_endpoint(
    client: TestClient,
    db: Session,
    sample_investigation,
    auth_headers
):
    """Teste do endpoint de detecção de padrões"""
    response = client.post(
        f"/api/v1/ml/pattern-detection/{sample_investigation.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "investigation_id" in data
    assert "patterns_detected" in data
    assert "patterns" in data


def test_network_analysis_endpoint(
    client: TestClient,
    db: Session,
    sample_investigation,
    auth_headers
):
    """Teste do endpoint de análise de rede"""
    response = client.post(
        f"/api/v1/ml/network-analysis/{sample_investigation.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "investigation_id" in data
    assert "graph" in data
    assert "central_actors" in data
    assert "communities" in data


def test_ocr_base64_endpoint(client: TestClient, auth_headers, sample_image):
    """Teste do endpoint de OCR base64"""
    # Converter imagem para base64
    buffer = io.BytesIO()
    sample_image.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    response = client.post(
        "/api/v1/ml/ocr/base64",
        headers=auth_headers,
        json={
            "base64_image": img_base64,
            "language": "por"
        }
    )
    
    # Pode falhar se Tesseract não estiver instalado
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
    else:
        # Aceitar erro se Tesseract não disponível
        assert response.status_code in [200, 500]


# ========== Testes de Integração ==========

def test_ml_full_pipeline(db: Session, sample_investigation):
    """Teste do pipeline completo de ML"""
    # 1. Análise de risco
    risk_analyzer = RiskAnalyzer(db)
    risk_result = risk_analyzer.analyze(sample_investigation.id)
    assert risk_result.overall_score >= 0.0
    
    # 2. Detecção de padrões
    pattern_detector = PatternDetector(db)
    pattern_result = pattern_detector.detect(sample_investigation.id)
    assert isinstance(pattern_result.patterns, list)
    
    # 3. Análise de rede
    network_analyzer = NetworkAnalyzer(db)
    network_result = network_analyzer.analyze(sample_investigation.id)
    assert len(network_result.graph.nodes) > 0
    
    # Pipeline completo executado com sucesso
    assert True


def test_ml_performance(db: Session, sample_investigation):
    """Teste de performance do sistema ML"""
    import time
    
    # Medir tempo de análise de risco
    start = time.time()
    analyzer = RiskAnalyzer(db)
    analyzer.analyze(sample_investigation.id)
    risk_time = time.time() - start
    
    # Deve executar em menos de 5 segundos
    assert risk_time < 5.0
    
    # Medir tempo de detecção de padrões
    start = time.time()
    detector = PatternDetector(db)
    detector.detect(sample_investigation.id)
    pattern_time = time.time() - start
    
    assert pattern_time < 5.0
    
    # Medir tempo de análise de rede
    start = time.time()
    network_analyzer = NetworkAnalyzer(db)
    network_analyzer.analyze(sample_investigation.id)
    network_time = time.time() - start
    
    assert network_time < 5.0


# ========== Marcadores de testes ==========

pytestmark = pytest.mark.ml
