"""
Testes para o Cartórios Scraper

Cobre:
- Busca por matrícula
- Busca por proprietário
- Busca por endereço
- Solicitação de certidão
- Verificação de ônus
- Cache
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.scrapers.cartorios_scraper import CartoriosScraper


@pytest.fixture
def cartorios_scraper():
    return CartoriosScraper()


@pytest.mark.asyncio
async def test_search_by_matricula(cartorios_scraper):
    """Testa busca por matrícula"""
    result = await cartorios_scraper.search_by_matricula(
        "12345",
        state="SP",
        city="São Paulo"
    )
    
    assert result is not None
    assert result["matricula"] == "12345"
    assert "imovel" in result
    assert "proprietarios" in result


@pytest.mark.asyncio
async def test_search_by_owner(cartorios_scraper):
    """Testa busca por proprietário"""
    results = await cartorios_scraper.search_by_owner(
        name="João Silva",
        state="SP"
    )
    
    assert isinstance(results, list)
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_search_by_owner_cpf(cartorios_scraper):
    """Testa busca por CPF do proprietário"""
    results = await cartorios_scraper.search_by_owner(
        cpf_cnpj="123.456.789-00",
        state="SP"
    )
    
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_search_by_address(cartorios_scraper):
    """Testa busca por endereço"""
    results = await cartorios_scraper.search_by_address(
        "Rua Exemplo, 123",
        "São Paulo",
        "SP"
    )
    
    assert isinstance(results, list)
    assert len(results) >= 0


@pytest.mark.asyncio
async def test_get_certidao(cartorios_scraper):
    """Testa solicitação de certidão"""
    certidao = await cartorios_scraper.get_certidao(
        "12345",
        "inteiro_teor"
    )
    
    assert certidao is not None
    assert "certidao_id" in certidao
    assert certidao["matricula"] == "12345"
    assert certidao["status"] == "Em processamento"


@pytest.mark.asyncio
async def test_verify_onus(cartorios_scraper):
    """Testa verificação de ônus"""
    result = await cartorios_scraper.verify_onus("12345")
    
    assert "matricula" in result
    assert "onus_encontrados" in result
    assert "total_onus" in result


def test_get_cartorio_info(cartorios_scraper):
    """Testa obtenção de informações do cartório"""
    info = cartorios_scraper.get_cartorio_info("SP", "São Paulo")
    
    assert "city" in info
    assert "state" in info
    assert "cartorios" in info
    assert len(info["cartorios"]) > 0


def test_cache(cartorios_scraper):
    """Testa sistema de cache"""
    key = "test_key"
    data = [{"matricula": "12345"}]
    
    cartorios_scraper._save_to_cache(key, data)
    cached = cartorios_scraper._get_from_cache(key)
    
    assert cached == data


def test_cache_expiration(cartorios_scraper):
    """Testa expiração do cache"""
    key = "test_key"
    data = [{"matricula": "12345"}]
    
    cartorios_scraper.cache_ttl = timedelta(seconds=-1)
    cartorios_scraper._save_to_cache(key, data)
    
    cached = cartorios_scraper._get_from_cache(key)
    assert cached is None


def test_clear_cache(cartorios_scraper):
    """Testa limpeza do cache"""
    cartorios_scraper._save_to_cache("key1", [{"a": 1}])
    assert len(cartorios_scraper.cache) >= 1
    
    cartorios_scraper.clear_cache()
    assert len(cartorios_scraper.cache) == 0


def test_cache_stats(cartorios_scraper):
    """Testa estatísticas do cache"""
    cartorios_scraper.clear_cache()
    cartorios_scraper._save_to_cache("key1", [{"a": 1}])
    
    stats = cartorios_scraper.get_cache_stats()
    
    assert stats["total_entries"] >= 1
    assert stats["ttl_hours"] == 72
