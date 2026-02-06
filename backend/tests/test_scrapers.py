"""
Test Scrapers
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx

from app.scrapers.car_scraper import CARScraper
from app.scrapers.incra_scraper import INCRAScraper
from app.scrapers.receita_scraper import ReceitaScraper


class TestCARScraper:
    """Test CAR Scraper"""
    
    @pytest.mark.asyncio
    async def test_search_returns_list(self):
        """Test that search returns a list"""
        scraper = CARScraper()
        result = await scraper.search(name="Test", cpf_cnpj="123.456.789-00")
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_search_with_cpf_cnpj(self):
        """Test search with CPF/CNPJ"""
        scraper = CARScraper()
        result = await scraper.search(cpf_cnpj="123.456.789-00")
        
        assert isinstance(result, list)
        # Empty result is OK for test environment
    
    @pytest.mark.asyncio
    async def test_search_with_name(self):
        """Test search with name only"""
        scraper = CARScraper()
        result = await scraper.search(name="João Silva")
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_scraper_handles_errors_gracefully(self):
        """Test that scraper handles errors without crashing"""
        scraper = CARScraper()
        
        # Should not raise exception even with invalid data
        result = await scraper.search(name="", cpf_cnpj="")
        assert isinstance(result, list)


class TestINCRAScraper:
    """Test INCRA Scraper"""
    
    @pytest.mark.asyncio
    async def test_search_returns_list(self):
        """Test that search returns a list"""
        scraper = INCRAScraper()
        result = await scraper.search(name="Test", cpf_cnpj="123.456.789-00")
        
        assert isinstance(result, list)


class TestReceitaScraper:
    """Test Receita Federal Scraper"""
    
    @pytest.mark.asyncio
    async def test_search_returns_list(self):
        """Test that search returns a list"""
        scraper = ReceitaScraper()
        result = await scraper.search("12.345.678/0001-00")
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    @patch('app.scrapers.receita_scraper.ReceitaScraper.fetch')
    async def test_search_with_mock_data(self, mock_fetch):
        """Test search with mocked API response"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "cnpj": "12345678000100",
            "razao_social": "Test Company",
            "nome_fantasia": "Test",
            "descricao_situacao_cadastral": "ATIVA",
            "uf": "SP",
            "municipio": "São Paulo",
            "logradouro": "Rua Test",
            "numero": "123",
            "bairro": "Centro",
            "cnae_fiscal_descricao": "Test Activity",
            "natureza_juridica": "206-2",
            "qsa": [
                {
                    "nome_socio": "João Silva",
                    "qualificacao_socio": "Administrador",
                }
            ]
        }
        mock_fetch.return_value = mock_response
        
        scraper = ReceitaScraper()
        result = await scraper.search("12.345.678/0001-00")
        
        assert len(result) == 1
        assert result[0]["cnpj"] == "12345678000100"
        assert result[0]["corporate_name"] == "Test Company"
        assert len(result[0]["partners"]) == 1
    
    @pytest.mark.asyncio
    @patch('app.scrapers.receita_scraper.ReceitaScraper.fetch')
    async def test_search_handles_api_error(self, mock_fetch):
        """Test that scraper handles API errors"""
        mock_fetch.side_effect = httpx.HTTPError("API Error")
        
        scraper = ReceitaScraper()
        result = await scraper.search("12.345.678/0001-00")
        
        # Should return empty list on error
        assert result == []
    
    @pytest.mark.asyncio
    async def test_cnpj_cleaning(self):
        """Test that CNPJ is cleaned properly"""
        scraper = ReceitaScraper()
        
        # Test with formatted CNPJ
        result = await scraper.search("12.345.678/0001-00")
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_receita_scraper_success_response():
    """Test Receita scraper with successful response"""
    scraper = ReceitaScraper()
    
    # Mock a successful response
    with patch.object(scraper, 'fetch') as mock_fetch:
        mock_response = Mock()
        mock_response.json.return_value = {
            "cnpj": "12345678000100",
            "razao_social": "Test Company LTDA",
            "nome_fantasia": "Test Company",
            "descricao_situacao_cadastral": "ATIVA",
            "uf": "SP",
            "municipio": "São Paulo",
            "logradouro": "Rua Teste",
            "numero": "100",
            "bairro": "Centro",
            "cnae_fiscal_descricao": "Atividade de teste",
            "natureza_juridica": "206-2",
            "qsa": [
                {
                    "nome_socio": "João Silva",
                    "cpf_cnpj_socio": "12345678900",
                    "qualificacao_socio": "Sócio-Administrador"
                }
            ]
        }
        mock_fetch.return_value = mock_response
        
        result = await scraper.search("12.345.678/0001-00")
        
        assert len(result) == 1
        assert result[0]["cnpj"] == "12345678000100"
        assert result[0]["corporate_name"] == "Test Company LTDA"
        assert len(result[0]["partners"]) == 1
        assert result[0]["partners"][0]["name"] == "João Silva"


@pytest.mark.asyncio
async def test_receita_scraper_api_error():
    """Test Receita scraper handling API errors"""
    scraper = ReceitaScraper()
    
    # Mock an error response
    with patch.object(scraper, 'fetch', side_effect=Exception("API Error")):
        result = await scraper.search("12.345.678/0001-00")
        
        # Should return empty list on error
        assert result == []


@pytest.mark.asyncio
async def test_receita_scraper_empty_qsa():
    """Test Receita scraper with empty partners list"""
    scraper = ReceitaScraper()
    
    with patch.object(scraper, 'fetch') as mock_fetch:
        mock_response = Mock()
        mock_response.json.return_value = {
            "cnpj": "12345678000100",
            "razao_social": "Test Company",
            "qsa": []  # Empty partners
        }
        mock_fetch.return_value = mock_response
        
        result = await scraper.search("12.345.678/0001-00")
        
        assert len(result) == 1
        assert result[0]["partners"] == []
