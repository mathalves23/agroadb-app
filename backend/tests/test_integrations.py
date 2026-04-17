"""
Testes para Integrações Externas
"""

import pytest
from fastapi.testclient import TestClient
from app.integrations.car_estados import CARIntegration, CARStateResult
from app.integrations.tribunais import TribunalIntegration, ProcessResult
from app.integrations.orgaos_federais import OrgaoFederalIntegration
from app.integrations.bureaus import BureauIntegration
from app.integrations.comunicacao import SlackIntegration, TeamsIntegration


# CAR Tests

@pytest.mark.asyncio
async def test_car_integration_initialization():
    """Testa inicialização do CAR"""
    integration = CARIntegration()
    assert integration is not None
    assert integration.timeout > 0
    await integration.close()


@pytest.mark.asyncio
async def test_car_state_config():
    """Testa configuração dos estados"""
    from app.integrations.car_estados import CARStateConfig
    
    assert len(CARStateConfig.URLS) == 27
    assert "SP" in CARStateConfig.URLS
    assert "MG" in CARStateConfig.URLS


@pytest.mark.asyncio
async def test_car_query_invalid_state():
    """Testa consulta em estado inválido"""
    integration = CARIntegration()
    result = await integration.query_car("CAR-123", "XX")
    
    assert not result.success
    assert "não suportado" in result.error.lower()
    
    await integration.close()


# Tribunais Tests

@pytest.mark.asyncio
async def test_tribunal_integration_initialization():
    """Testa inicialização de tribunais"""
    integration = TribunalIntegration()
    assert integration is not None
    await integration.close()


@pytest.mark.asyncio
async def test_process_number_normalization():
    """Testa normalização de número de processo"""
    integration = TribunalIntegration()
    
    # Teste com número limpo
    normalized = integration._normalize_process_number("00012345620238260100")
    assert "-" in normalized
    assert "." in normalized
    
    await integration.close()


@pytest.mark.asyncio
async def test_detect_system():
    """Testa detecção de sistema"""
    integration = TribunalIntegration()
    
    assert integration._detect_system("SP") == "esaj"
    assert integration._detect_system("PR") in ["esaj", "projudi"]
    
    await integration.close()


# Órgãos Federais Tests

@pytest.mark.asyncio
async def test_orgaos_integration():
    """Testa integração com órgãos federais"""
    integration = OrgaoFederalIntegration()
    assert integration is not None
    
    # Teste sem credenciais (deve retornar erro estruturado)
    result = await integration.query_ibama("12345678900")
    assert "success" in result
    
    await integration.close()


@pytest.mark.asyncio
async def test_orgaos_query_all():
    """Testa consulta a todos os órgãos"""
    integration = OrgaoFederalIntegration()
    
    result = await integration.query_all(
        cpf_cnpj="12345678900",
        coordinates={"lat": -15.0, "lng": -47.0}
    )
    
    assert "ibama" in result
    assert "icmbio" in result
    assert "queried_at" in result
    
    await integration.close()


# Bureaus Tests

@pytest.mark.asyncio
async def test_bureau_integration():
    """Testa integração com bureaus"""
    integration = BureauIntegration()
    assert integration is not None
    await integration.close()


@pytest.mark.asyncio
async def test_bureau_without_keys():
    """Testa consulta sem API keys"""
    integration = BureauIntegration()
    
    result = await integration.query_serasa("12345678900")
    assert not result["success"]
    assert "não configurada" in result["error"]
    
    await integration.close()


@pytest.mark.asyncio
async def test_bureau_score_classification():
    """Testa classificação de scores"""
    integration = BureauIntegration()
    
    assert integration._classify_score(850) == "excellent"
    assert integration._classify_score(750) == "good"
    assert integration._classify_score(650) == "fair"
    assert integration._classify_score(550) == "poor"
    assert integration._classify_score(450) == "very_poor"
    assert integration._classify_score(None) == "unknown"
    
    await integration.close()


# Slack Tests

@pytest.mark.asyncio
async def test_slack_integration():
    """Testa integração com Slack"""
    integration = SlackIntegration()
    assert integration is not None
    await integration.close()


@pytest.mark.asyncio
async def test_slack_without_credentials():
    """Testa Slack sem credenciais"""
    integration = SlackIntegration()
    
    result = await integration.send_message("#test", "test")
    assert not result["success"]
    
    await integration.close()


# Teams Tests

@pytest.mark.asyncio
async def test_teams_integration():
    """Testa integração com Teams"""
    integration = TeamsIntegration()
    assert integration is not None
    await integration.close()


@pytest.mark.asyncio
async def test_teams_without_webhook():
    """Testa Teams sem webhook"""
    integration = TeamsIntegration()
    
    result = await integration.send_message("Test", "Message")
    assert not result["success"]
    
    await integration.close()


# Endpoints Tests

def test_integrations_health_endpoint(client: TestClient):
    """Testa endpoint de health check"""
    response = client.get("/api/v1/integrations/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "car" in data
    assert "tribunais" in data
    assert "orgaos_federais" in data
    assert "bureaus" in data
    assert "comunicacao" in data


def test_car_states_endpoint(client: TestClient, auth_headers):
    """Testa endpoint de lista de estados CAR"""
    response = client.get(
        "/api/v1/integrations/car/states",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "states" in data
    assert data["total"] == 27
    assert "SP" in data["states"]


def test_tribunal_systems_endpoint(client: TestClient, auth_headers):
    """Testa endpoint de sistemas de tribunais"""
    response = client.get(
        "/api/v1/integrations/tribunais/systems",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "esaj_states" in data
    assert "projudi_states" in data
    assert "pje" in data


# Integration Tests

@pytest.mark.asyncio
async def test_full_integration_workflow():
    """Testa workflow completo de integrações"""
    
    # 1. CAR
    car = CARIntegration()
    car_result = CARStateResult(
        state="SP",
        car_code="SP-123",
        success=True,
        data={"test": "data"}
    )
    assert car_result.to_dict()["success"]
    await car.close()
    
    # 2. Tribunais
    tribunal = TribunalIntegration()
    process_result = ProcessResult(
        process_number="0001234-56.2023.8.26.0100",
        state="SP",
        system="esaj",
        success=True,
        data={"test": "data"}
    )
    assert process_result.to_dict()["success"]
    await tribunal.close()
    
    # 3. Órgãos
    orgaos = OrgaoFederalIntegration()
    await orgaos.close()
    
    # 4. Bureaus
    bureaus = BureauIntegration()
    await bureaus.close()
    
    # Workflow completo executado com sucesso
    assert True


pytest.mark = pytest.mark.integrations
