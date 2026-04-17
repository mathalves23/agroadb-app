"""
Testes para o Diário Oficial Scraper

Cobre:
- Busca geral
- Busca por CPF/CNPJ
- Busca por nome
- Filtros de data e tipo
- Monitoramento de termos
- Cache
"""
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.scrapers.diario_oficial_scraper import DiarioOficialScraper


@pytest.fixture
def diario_scraper():
    return DiarioOficialScraper()


@pytest.mark.asyncio
async def test_search_basic(diario_scraper):
    """Testa busca básica"""
    with patch.object(diario_scraper, '_search_jusbrasil', new_callable=AsyncMock) as mock_jb, \
         patch.object(diario_scraper, '_search_dou', new_callable=AsyncMock) as mock_dou:
        
        mock_jb.return_value = [{"id": "jb1", "content": "test"}]
        mock_dou.return_value = [{"id": "dou1", "content": "test"}]
        
        results = await diario_scraper.search("Teste")
        
        assert len(results) == 2
        mock_jb.assert_called_once()
        mock_dou.assert_called_once()


@pytest.mark.asyncio
async def test_search_by_cpf_cnpj(diario_scraper):
    """Testa busca por CPF/CNPJ"""
    with patch.object(diario_scraper, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{"id": "pub1"}]
        
        results = await diario_scraper.search_by_cpf_cnpj("12.345.678/0001-90")
        
        assert len(results) >= 1
        assert mock_search.call_count >= 2  # Formato limpo + formatado


@pytest.mark.asyncio
async def test_search_by_name(diario_scraper):
    """Testa busca por nome"""
    with patch.object(diario_scraper, 'search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{"id": "pub1", "title": "João Silva"}]
        
        results = await diario_scraper.search_by_name("João Silva")
        
        assert len(results) > 0
        mock_search.assert_called_once()


def test_extract_keywords(diario_scraper):
    """Testa extração de keywords"""
    keywords = diario_scraper._extract_keywords("João Silva empresa teste")
    
    assert "joão" in keywords or "silva" in keywords
    assert len(keywords) <= 10


def test_remove_duplicates(diario_scraper):
    """Testa remoção de duplicatas"""
    results = [
        {"id": "1", "title": "A"},
        {"id": "2", "title": "B"},
        {"id": "1", "title": "A"},  # Duplicata
    ]
    
    unique = diario_scraper._remove_duplicates(results)
    
    assert len(unique) == 2


def test_get_diary_types(diario_scraper):
    """Testa obtenção de tipos de diários"""
    types = diario_scraper.get_diary_types()
    
    assert "DOU" in types
    assert "DOE" in types
    assert "DOM" in types


@pytest.mark.asyncio
async def test_monitor_term(diario_scraper):
    """Testa configuração de monitoramento"""
    config = await diario_scraper.monitor_term("João Silva", "DOU")
    
    assert "monitor_id" in config
    assert config["term"] == "João Silva"
    assert config["active"] is True


def test_cache(diario_scraper):
    """Testa sistema de cache"""
    key = "test_key"
    data = [{"id": "1"}]
    
    diario_scraper._save_to_cache(key, data)
    cached = diario_scraper._get_from_cache(key)
    
    assert cached == data


def test_cache_stats(diario_scraper):
    """Testa estatísticas do cache"""
    diario_scraper._save_to_cache("key1", [{"a": 1}])
    
    stats = diario_scraper.get_cache_stats()
    
    assert stats["total_entries"] >= 1
    assert stats["ttl_hours"] == 24
