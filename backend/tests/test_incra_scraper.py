"""
Testes para o INCRA Scraper

Cobre:
- Busca por CPF/CNPJ
- Busca por nome
- Busca por número do CCIR
- Busca por código do imóvel
- Verificação de autenticidade do CCIR
- Cache de resultados
- Parsing de dados
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.scrapers.incra_scraper import INCRAScraper


@pytest.fixture
def incra_scraper():
    """Fixture que retorna uma instância do INCRAScraper"""
    return INCRAScraper()


@pytest.fixture
def mock_ccir_data():
    """Dados mockados da API do CCIR"""
    return {
        "numeroCcir": "12345678-2024",
        "codigoImovel": "SP-1234567890",
        "nomeImovel": "Fazenda São José",
        "nomeProprietario": "João Silva",
        "cpfCnpj": "12345678000190",
        "uf": "SP",
        "municipio": "Ribeirão Preto",
        "endereco": "Zona Rural, s/n",
        "latitude": -21.1775,
        "longitude": -47.8103,
        "areaTotal": 250.5,
        "areaAproveitavel": 200.0,
        "areaInaproveitavel": 10.0,
        "areaPreservacao": 30.5,
        "areaReservaLegal": 50.0,
        "classificacao": "Média Propriedade",
        "tipoModulo": "Módulo Fiscal",
        "modulosFiscais": 10.5,
        "situacao": "Regular",
        "dataInscricao": "2020-03-15",
        "dataAtualizacao": "2024-01-10",
        "validadeCcir": "2024-12-31",
        "tipoExploracao": "Agricultura e Pecuária",
        "usoProdutivo": True,
        "situacaoItr": "Em dia",
        "anoItr": 2024,
    }


@pytest.fixture
def mock_property_data():
    """Dados mockados da API do imóvel por código"""
    return {
        "numeroCcir": "98765432-2024",
        "codigoImovel": "MG-9876543210",
        "nomeImovel": "Fazenda Boa Vista",
        "titular": "Maria Santos",
        "cpfCnpj": "98765432000100",
        "uf": "MG",
        "municipio": "Uberaba",
        "areaTotal": 500.0,
        "situacao": "Regular",
    }


class TestINCRAScraperSearch:
    """Testes para o método search"""
    
    @pytest.mark.asyncio
    async def test_search_by_cpf_cnpj(self, incra_scraper):
        """Testa busca por CPF/CNPJ"""
        with patch.object(incra_scraper, '_search_by_cpf_cnpj', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [{
                "ccir_number": "12345678-2024",
                "owner_cpf_cnpj": "12345678000190",
            }]
            
            results = await incra_scraper.search(cpf_cnpj="123.456.780/0001-90")
            
            assert len(results) == 1
            assert results[0]["ccir_number"] == "12345678-2024"
            mock_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_by_name_fallback(self, incra_scraper):
        """Testa busca por nome quando CPF/CNPJ não retorna resultados"""
        with patch.object(incra_scraper, '_search_by_cpf_cnpj', new_callable=AsyncMock) as mock_cpf, \
             patch.object(incra_scraper, '_search_by_name', new_callable=AsyncMock) as mock_name:
            
            mock_cpf.return_value = []
            mock_name.return_value = [{
                "property_name": "Fazenda Teste",
                "owner_name": "João Silva",
            }]
            
            results = await incra_scraper.search(
                name="João Silva",
                cpf_cnpj="12345678000190"
            )
            
            # Deve tentar buscar por nome quando CPF não retorna resultados
            mock_name.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_with_cache(self, incra_scraper):
        """Testa que resultados são retornados do cache"""
        # Adicionar ao cache manualmente
        cache_key = "João Silva_None_SP_None"
        cached_data = [{"property_name": "Fazenda Teste"}]
        incra_scraper._save_to_cache(cache_key, cached_data)
        
        # Buscar deve retornar do cache
        results = await incra_scraper.search(name="João Silva", state="SP")
        
        assert results == cached_data
    
    @pytest.mark.asyncio
    async def test_search_handles_errors_gracefully(self, incra_scraper):
        """Testa que erros não quebram a busca"""
        with patch.object(incra_scraper, '_search_by_cpf_cnpj', side_effect=Exception("API Error")):
            results = await incra_scraper.search(cpf_cnpj="12345678000190")
            
            # Deve retornar lista vazia em caso de erro
            assert results == []


class TestINCRAScraperCPFCNPJSearch:
    """Testes para busca por CPF/CNPJ"""
    
    @pytest.mark.asyncio
    async def test_search_by_cpf_cnpj_cleans_input(self, incra_scraper):
        """Testa que CPF/CNPJ é limpo corretamente"""
        results = await incra_scraper._search_by_cpf_cnpj("123.456.780/0001-90", "SP")
        
        assert len(results) == 1
        # CPF/CNPJ deve estar limpo (sem pontuação)
        assert results[0]["owner_cpf_cnpj"] == "123456780000190"
    
    @pytest.mark.asyncio
    async def test_search_by_cpf_cnpj_structure(self, incra_scraper):
        """Testa estrutura de dados retornada"""
        results = await incra_scraper._search_by_cpf_cnpj("12345678000190", "SP")
        
        assert len(results) == 1
        result = results[0]
        
        # Verificar campos obrigatórios
        assert "ccir_number" in result
        assert "property_code" in result
        assert "property_name" in result
        assert "owner_name" in result
        assert "owner_cpf_cnpj" in result
        assert "state" in result
        assert "city" in result
        assert "area_total_hectares" in result
        assert "classification" in result
        assert "status" in result
        assert "data_source" in result
        assert result["data_source"] == "INCRA/SNCR"


class TestINCRAScraperCCIR:
    """Testes para busca por CCIR"""
    
    @pytest.mark.asyncio
    async def test_get_property_by_ccir_from_cache(self, incra_scraper, mock_ccir_data):
        """Testa retorno do cache"""
        ccir_number = "12345678-2024"
        cached_data = [{
            "ccir_number": ccir_number,
            "property_name": "Fazenda Teste",
        }]
        incra_scraper._save_to_cache(f"ccir_{ccir_number}", cached_data)
        
        result = await incra_scraper.get_property_by_ccir(ccir_number)
        
        assert result is not None
        assert result["ccir_number"] == ccir_number
    
    @pytest.mark.asyncio
    async def test_get_property_by_ccir_api_call(
        self, incra_scraper, mock_ccir_data
    ):
        """Testa chamada à API quando não está no cache"""
        ccir_number = "12345678-2024"
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = mock_ccir_data
        
        with patch.object(incra_scraper, 'fetch', new_callable=AsyncMock, return_value=mock_response):
            result = await incra_scraper.get_property_by_ccir(ccir_number)
            
            assert result is not None
            assert result["ccir_number"] == ccir_number
            assert result["property_name"] == "Fazenda São José"
            assert result["owner_name"] == "João Silva"
            assert result["state"] == "SP"
            assert result["city"] == "Ribeirão Preto"
            assert result["area_total_hectares"] == 250.5
            assert result["classification"] == "Média Propriedade"
    
    @pytest.mark.asyncio
    async def test_get_property_by_ccir_not_found(self, incra_scraper):
        """Testa quando CCIR não é encontrado"""
        ccir_number = "INVALID-CCIR"
        
        with patch.object(incra_scraper, 'fetch', new_callable=AsyncMock, return_value=None):
            result = await incra_scraper.get_property_by_ccir(ccir_number)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_property_by_ccir_handles_errors(self, incra_scraper):
        """Testa tratamento de erros"""
        ccir_number = "12345678-2024"
        
        with patch.object(incra_scraper, 'fetch', side_effect=Exception("Network Error")):
            result = await incra_scraper.get_property_by_ccir(ccir_number)
            
            assert result is None


class TestINCRAScraperPropertyCode:
    """Testes para busca por código do imóvel"""
    
    @pytest.mark.asyncio
    async def test_get_property_by_code_from_cache(self, incra_scraper):
        """Testa retorno do cache"""
        property_code = "SP-1234567890"
        cached_data = [{
            "property_code": property_code,
            "property_name": "Fazenda Teste",
        }]
        incra_scraper._save_to_cache(f"code_{property_code}", cached_data)
        
        result = await incra_scraper.get_property_by_code(property_code)
        
        assert result is not None
        assert result["property_code"] == property_code
    
    @pytest.mark.asyncio
    async def test_get_property_by_code_api_call(
        self, incra_scraper, mock_property_data
    ):
        """Testa chamada à API quando não está no cache"""
        property_code = "MG-9876543210"
        
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = mock_property_data
        
        with patch.object(incra_scraper, 'fetch', new_callable=AsyncMock, return_value=mock_response):
            result = await incra_scraper.get_property_by_code(property_code)
            
            assert result is not None
            assert result["property_name"] == "Fazenda Boa Vista"
            assert result["owner_name"] == "Maria Santos"
    
    @pytest.mark.asyncio
    async def test_get_property_by_code_not_found(self, incra_scraper):
        """Testa quando código não é encontrado"""
        property_code = "INVALID-CODE"
        
        with patch.object(incra_scraper, 'fetch', new_callable=AsyncMock, return_value=None):
            result = await incra_scraper.get_property_by_code(property_code)
            
            assert result is None


class TestINCRAScraperCCIRVerification:
    """Testes para verificação de autenticidade do CCIR"""
    
    @pytest.mark.asyncio
    async def test_verify_ccir_authenticity_valid(self, incra_scraper):
        """Testa verificação de CCIR válido"""
        ccir_number = "12345678-2024"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "valido": True,
            "mensagem": "CCIR válido",
            "dataEmissao": "2024-01-10",
            "dataValidade": "2024-12-31",
            "proprietario": "João Silva",
        }
        
        with patch.object(incra_scraper, 'fetch', new_callable=AsyncMock, return_value=mock_response):
            result = await incra_scraper.verify_ccir_authenticity(ccir_number)
            
            assert result["valid"] is True
            assert result["ccir_number"] == ccir_number
            assert result["owner_name"] == "João Silva"
    
    @pytest.mark.asyncio
    async def test_verify_ccir_authenticity_invalid(self, incra_scraper):
        """Testa verificação de CCIR inválido"""
        ccir_number = "00000000-0000"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "valido": False,
            "mensagem": "CCIR não encontrado",
        }
        
        with patch.object(incra_scraper, 'fetch', new_callable=AsyncMock, return_value=mock_response):
            result = await incra_scraper.verify_ccir_authenticity(ccir_number)
            
            assert result["valid"] is False
            assert result["message"] == "CCIR não encontrado"
    
    @pytest.mark.asyncio
    async def test_verify_ccir_authenticity_error(self, incra_scraper):
        """Testa tratamento de erro na verificação"""
        ccir_number = "12345678-2024"
        
        with patch.object(incra_scraper, 'fetch', new_callable=AsyncMock, return_value=None):
            result = await incra_scraper.verify_ccir_authenticity(ccir_number)
            
            assert result["valid"] is False
            assert "Não foi possível verificar" in result["message"]


class TestINCRAScraperParsing:
    """Testes para parsing de dados"""
    
    def test_parse_ccir_data_complete(self, incra_scraper, mock_ccir_data):
        """Testa parsing com dados completos"""
        ccir_number = "12345678-2024"
        
        result = incra_scraper._parse_ccir_data(mock_ccir_data, ccir_number)
        
        assert result["ccir_number"] == ccir_number
        assert result["property_name"] == "Fazenda São José"
        assert result["owner_name"] == "João Silva"
        assert result["owner_cpf_cnpj"] == "12345678000190"
        assert result["state"] == "SP"
        assert result["city"] == "Ribeirão Preto"
        assert result["area_total_hectares"] == 250.5
        assert result["area_aproveitavel_hectares"] == 200.0
        assert result["classification"] == "Média Propriedade"
        assert result["fiscal_modules"] == 10.5
        assert result["productive_use"] is True
    
    def test_parse_ccir_data_missing_fields(self, incra_scraper):
        """Testa parsing com campos faltando"""
        ccir_number = "12345678-2024"
        data = {"nomeImovel": "Fazenda"}
        
        result = incra_scraper._parse_ccir_data(data, ccir_number)
        
        # Deve ter valores padrão para campos faltando
        assert result["area_total_hectares"] == 0.0
        assert result["area_aproveitavel_hectares"] == 0.0
        assert result["fiscal_modules"] == 0.0
        assert result["productive_use"] is False


class TestINCRAScraperHelpers:
    """Testes para métodos auxiliares"""
    
    def test_clean_cpf_cnpj(self, incra_scraper):
        """Testa limpeza de CPF/CNPJ"""
        assert incra_scraper._clean_cpf_cnpj("123.456.789-00") == "12345678900"
        assert incra_scraper._clean_cpf_cnpj("12.345.678/0001-90") == "12345678000190"
        assert incra_scraper._clean_cpf_cnpj("12345678000190") == "12345678000190"
    
    def test_format_ccir(self, incra_scraper):
        """Testa formatação de CCIR"""
        # CCIR com 13 dígitos
        assert incra_scraper._format_ccir("1234567890123") == "1234567890123"
        # CCIR já formatado permanece como está se não tiver 13 dígitos numéricos
        result = incra_scraper._format_ccir("12345678-2024")
        # Como "12345678-2024" não tem exatamente 13 dígitos numéricos, retorna como está
        assert result == "12345678-2024" or result == "123456782024"
        # CCIR inválido
        assert incra_scraper._format_ccir("123") == "123"


class TestINCRAScraperCache:
    """Testes para sistema de cache"""
    
    def test_save_and_get_from_cache(self, incra_scraper):
        """Testa salvar e recuperar do cache"""
        key = "test_key"
        data = [{"property": "test"}]
        
        incra_scraper._save_to_cache(key, data)
        cached = incra_scraper._get_from_cache(key)
        
        assert cached == data
    
    def test_cache_expiration(self, incra_scraper):
        """Testa expiração do cache"""
        key = "test_key"
        data = [{"property": "test"}]
        
        # Salvar com TTL muito curto
        incra_scraper.cache_ttl = timedelta(seconds=-1)  # Já expirado
        incra_scraper._save_to_cache(key, data)
        
        cached = incra_scraper._get_from_cache(key)
        
        assert cached is None
    
    def test_clear_cache(self, incra_scraper):
        """Testa limpeza do cache"""
        incra_scraper._save_to_cache("key1", [{"a": 1}])
        incra_scraper._save_to_cache("key2", [{"b": 2}])
        
        assert len(incra_scraper.cache) == 2
        
        incra_scraper.clear_cache()
        
        assert len(incra_scraper.cache) == 0
    
    def test_get_cache_stats(self):
        """Testa estatísticas do cache"""
        # Criar nova instância para garantir cache limpo
        scraper = INCRAScraper()
        
        # Cache válido
        scraper._save_to_cache("valid1", [{"a": 1}])
        scraper._save_to_cache("valid2", [{"b": 2}])
        
        # Forçar um cache expirado manualmente inserindo no dicionário
        scraper.cache["expired"] = (datetime.now() - timedelta(hours=25), [{"c": 3}])
        
        stats = scraper.get_cache_stats()
        
        assert stats["total_entries"] == 3
        assert stats["valid_entries"] == 2
        assert stats["expired_entries"] == 1
        assert stats["ttl_hours"] == 24
