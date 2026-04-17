"""
Testes para o Receita Federal Scraper

Cobre:
- Busca por CNPJ com múltiplas APIs
- Sistema de fallback entre APIs
- Extração de estrutura societária (QSA)
- Análise de CNPJs relacionados
- Estrutura corporativa recursiva
- Análise de rede corporativa
- Cache de resultados
- Rate limiting
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.scrapers.receita_scraper import ReceitaScraper, APIProvider


@pytest.fixture
def receita_scraper():
    """Fixture que retorna uma instância do ReceitaScraper"""
    return ReceitaScraper()


@pytest.fixture
def mock_company_data_brasilapi():
    """Dados mockados da BrasilAPI"""
    return {
        "cnpj": "12345678000190",
        "razao_social": "EMPRESA TESTE LTDA",
        "nome_fantasia": "Empresa Teste",
        "descricao_situacao_cadastral": "ATIVA",
        "data_situacao_cadastral": "2020-01-15",
        "uf": "SP",
        "municipio": "São Paulo",
        "bairro": "Centro",
        "logradouro": "Rua Teste",
        "numero": "123",
        "complemento": "Sala 456",
        "cep": "01234567",
        "ddd_telefone_1": "1133334444",
        "email": "contato@empresateste.com.br",
        "cnae_fiscal": "6201500",
        "cnae_fiscal_descricao": "Desenvolvimento de programas de computador sob encomenda",
        "codigo_natureza_juridica": "2062",
        "natureza_juridica": "Sociedade Empresária Limitada",
        "porte": "DEMAIS",
        "capital_social": "100000.00",
        "data_inicio_atividade": "2020-01-10",
        "identificador_matriz_filial": "1",
        "qsa": [
            {
                "nome_socio": "JOÃO SILVA",
                "cpf_cnpj_socio": "***123456**",
                "codigo_qualificacao_socio": "49",
                "qualificacao_socio": "Sócio-Administrador",
                "data_entrada_sociedade": "2020-01-10",
                "pais_socio": "Brasil",
                "percentual_capital_social": "60.00",
            },
            {
                "nome_socio": "MARIA SANTOS",
                "cpf_cnpj_socio": "***987654**",
                "codigo_qualificacao_socio": "49",
                "qualificacao_socio": "Sócio-Administrador",
                "data_entrada_sociedade": "2020-01-10",
                "pais_socio": "Brasil",
                "percentual_capital_social": "40.00",
            },
            {
                "nome_socio": "EMPRESA HOLDING LTDA",
                "cpf_cnpj_socio": "98765432000100",
                "codigo_qualificacao_socio": "22",
                "qualificacao_socio": "Sócio",
                "data_entrada_sociedade": "2021-06-15",
                "pais_socio": "Brasil",
                "percentual_capital_social": "30.00",
            },
        ],
        "cnaes_secundarios": [
            {
                "codigo": "6202300",
                "descricao": "Desenvolvimento e licenciamento de programas de computador customizáveis",
            },
        ],
    }


@pytest.fixture
def mock_company_data_receitaws():
    """Dados mockados da ReceitaWS"""
    return {
        "cnpj": "12.345.678/0001-90",
        "nome": "EMPRESA TESTE LTDA",
        "fantasia": "Empresa Teste",
        "situacao": "ATIVA",
        "uf": "SP",
        "municipio": "São Paulo",
        "bairro": "Centro",
        "logradouro": "Rua Teste",
        "numero": "123",
        "cep": "01234-567",
        "telefone": "(11) 3333-4444",
        "email": "contato@empresateste.com.br",
        "abertura": "10/01/2020",
        "tipo": "MATRIZ",
        "qsa": [
            {
                "nome": "JOÃO SILVA",
                "qualificacao": "Sócio-Administrador",
            },
        ],
    }


class TestReceitaScraperBasicSearch:
    """Testes para busca básica"""
    
    @pytest.mark.asyncio
    async def test_search_valid_cnpj(self, receita_scraper, mock_company_data_brasilapi):
        """Testa busca com CNPJ válido"""
        with patch.object(receita_scraper, '_fetch_from_provider', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_company_data_brasilapi
            
            results = await receita_scraper.search("12.345.678/0001-90")
            
            assert len(results) == 1
            assert results[0]["cnpj_clean"] == "12345678000190"
            assert results[0]["corporate_name"] == "EMPRESA TESTE LTDA"
    
    @pytest.mark.asyncio
    async def test_search_invalid_cnpj(self, receita_scraper):
        """Testa busca com CNPJ inválido"""
        results = await receita_scraper.search("123")  # CNPJ muito curto
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_search_with_cache(self, receita_scraper, mock_company_data_brasilapi):
        """Testa que busca usa cache em segunda chamada"""
        with patch.object(receita_scraper, '_fetch_from_provider', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_company_data_brasilapi
            
            # Primeira busca
            results1 = await receita_scraper.search("12345678000190")
            assert len(results1) == 1
            
            # Segunda busca deve usar cache
            results2 = await receita_scraper.search("12345678000190")
            assert len(results2) == 1
            
            # Deve ter chamado API apenas uma vez
            assert mock_fetch.call_count == 1


class TestReceitaScraperFallback:
    """Testes para sistema de fallback entre APIs"""
    
    @pytest.mark.asyncio
    async def test_fallback_to_second_api(self, receita_scraper, mock_company_data_receitaws):
        """Testa fallback quando primeira API falha"""
        async def mock_fetch_side_effect(provider, cnpj):
            if provider == APIProvider.BRASILAPI:
                return None  # Primeira API falha
            elif provider == APIProvider.RECEITAWS:
                return mock_company_data_receitaws  # Segunda API funciona
            return None
        
        with patch.object(receita_scraper, '_fetch_from_provider', side_effect=mock_fetch_side_effect):
            results = await receita_scraper.search("12345678000190")
            
            assert len(results) == 1
            assert results[0]["provider"] == "ReceitaWS"
    
    @pytest.mark.asyncio
    async def test_all_apis_fail(self, receita_scraper):
        """Testa quando todas as APIs falham"""
        with patch.object(receita_scraper, '_fetch_from_provider', new_callable=AsyncMock, return_value=None):
            results = await receita_scraper.search("12345678000190")
            
            assert results == []


class TestReceitaScraperDataProcessing:
    """Testes para processamento de dados"""
    
    def test_process_company_data_complete(self, receita_scraper, mock_company_data_brasilapi):
        """Testa processamento de dados completos"""
        result = receita_scraper._process_company_data(
            mock_company_data_brasilapi,
            APIProvider.BRASILAPI
        )
        
        assert result["cnpj"] == "12.345.678/0001-90"
        assert result["cnpj_clean"] == "12345678000190"
        assert result["corporate_name"] == "EMPRESA TESTE LTDA"
        assert result["trade_name"] == "Empresa Teste"
        assert result["status"] == "ATIVA"
        assert result["state"] == "SP"
        assert result["city"] == "São Paulo"
        assert result["capital"] == 100000.0
        assert result["is_matriz"] is True
        assert result["partners_count"] == 3
        assert result["provider"] == "BrasilAPI"
    
    def test_extract_partners(self, receita_scraper, mock_company_data_brasilapi):
        """Testa extração de sócios"""
        partners = receita_scraper._extract_partners(
            mock_company_data_brasilapi,
            APIProvider.BRASILAPI
        )
        
        assert len(partners) == 3
        assert partners[0]["name"] == "JOÃO SILVA"
        assert partners[0]["qualification"]["description"] == "Sócio-Administrador"
        assert partners[0]["percentage"] == "60.00"
        
        # Sócio PJ
        assert partners[2]["name"] == "EMPRESA HOLDING LTDA"
        assert partners[2]["cpf_cnpj"] == "98765432000100"
    
    def test_extract_related_cnpjs(self, receita_scraper, mock_company_data_brasilapi):
        """Testa extração de CNPJs relacionados"""
        partners = receita_scraper._extract_partners(
            mock_company_data_brasilapi,
            APIProvider.BRASILAPI
        )
        
        related = receita_scraper._extract_related_cnpjs(
            mock_company_data_brasilapi,
            partners
        )
        
        # Deve identificar sócio PJ
        assert len(related) >= 1
        cnpj_socio_pj = [r for r in related if r["relationship"] == "Sócio PJ"]
        assert len(cnpj_socio_pj) == 1
        assert cnpj_socio_pj[0]["cnpj_clean"] == "98765432000100"


class TestReceitaScraperHelpers:
    """Testes para métodos auxiliares"""
    
    def test_clean_cnpj(self, receita_scraper):
        """Testa limpeza de CNPJ"""
        assert receita_scraper._clean_cnpj("12.345.678/0001-90") == "12345678000190"
        assert receita_scraper._clean_cnpj("12345678000190") == "12345678000190"
        assert receita_scraper._clean_cnpj("  12.345.678/0001-90  ") == "12345678000190"
    
    def test_format_cnpj(self, receita_scraper):
        """Testa formatação de CNPJ"""
        assert receita_scraper._format_cnpj("12345678000190") == "12.345.678/0001-90"
        assert receita_scraper._format_cnpj("12.345.678/0001-90") == "12.345.678/0001-90"
    
    def test_validate_cnpj(self, receita_scraper):
        """Testa validação de CNPJ"""
        assert receita_scraper._validate_cnpj("12345678000190") is True
        assert receita_scraper._validate_cnpj("12.345.678/0001-90") is True
        assert receita_scraper._validate_cnpj("123") is False
        assert receita_scraper._validate_cnpj("abc") is False
    
    def test_format_address(self, receita_scraper):
        """Testa formatação de endereço"""
        data = {
            "logradouro": "Rua Teste",
            "numero": "123",
            "complemento": "Sala 456",
        }
        address = receita_scraper._format_address(data)
        assert address == "Rua Teste, 123, Sala 456"
    
    def test_clean_cpf_cnpj_with_protection(self, receita_scraper):
        """Testa limpeza de CPF/CNPJ com proteção LGPD"""
        assert receita_scraper._clean_cpf_cnpj("***123456**") == "123456"
        assert receita_scraper._clean_cpf_cnpj("12345678000190") == "12345678000190"


class TestReceitaScraperRateLimiting:
    """Testes para rate limiting"""
    
    def test_can_make_request_no_limit(self, receita_scraper):
        """Testa requisição sem rate limit"""
        assert receita_scraper._can_make_request(APIProvider.BRASILAPI) is True
    
    def test_can_make_request_with_limit(self, receita_scraper):
        """Testa requisição com rate limit"""
        # Primeira requisição sempre pode
        assert receita_scraper._can_make_request(APIProvider.RECEITAWS) is True
        
        # Marcar requisição
        receita_scraper._mark_request(APIProvider.RECEITAWS)
        
        # Imediatamente após, não pode (rate limit = 3 req/min)
        assert receita_scraper._can_make_request(APIProvider.RECEITAWS) is False
    
    def test_rate_limit_expires(self, receita_scraper):
        """Testa que rate limit expira após tempo adequado"""
        # Marcar requisição antiga
        receita_scraper.last_request[APIProvider.RECEITAWS] = datetime.now() - timedelta(seconds=30)
        
        # Deve poder fazer requisição (3 req/min = 20s de intervalo)
        assert receita_scraper._can_make_request(APIProvider.RECEITAWS) is True


class TestReceitaScraperCorporateStructure:
    """Testes para estrutura corporativa"""
    
    @pytest.mark.asyncio
    async def test_get_full_corporate_structure(self, receita_scraper, mock_company_data_brasilapi):
        """Testa busca de estrutura corporativa"""
        with patch.object(receita_scraper, '_fetch_from_provider', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_company_data_brasilapi
            
            structure = await receita_scraper.get_full_corporate_structure(
                "12345678000190",
                depth=1
            )
            
            assert "company" in structure
            assert "related_companies" in structure
            assert structure["depth_level"] == 1
            assert structure["company"]["cnpj_clean"] == "12345678000190"
    
    @pytest.mark.asyncio
    async def test_get_full_corporate_structure_depth_zero(self, receita_scraper):
        """Testa estrutura com profundidade zero"""
        structure = await receita_scraper.get_full_corporate_structure(
            "12345678000190",
            depth=0
        )
        
        assert structure == {}
    
    @pytest.mark.asyncio
    async def test_analyze_corporate_network(self, receita_scraper, mock_company_data_brasilapi):
        """Testa análise de rede corporativa"""
        with patch.object(receita_scraper, '_fetch_from_provider', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_company_data_brasilapi
            
            analysis = await receita_scraper.analyze_corporate_network("12345678000190")
            
            assert "root_cnpj" in analysis
            assert "total_companies" in analysis
            assert "all_cnpjs" in analysis
            assert "total_partners" in analysis
            assert "common_partners" in analysis
            assert "corporate_structure" in analysis
            
            assert analysis["root_cnpj"] == "12345678000190"
            assert analysis["total_companies"] >= 1


class TestReceitaScraperCache:
    """Testes para sistema de cache"""
    
    def test_save_and_get_from_cache(self, receita_scraper):
        """Testa salvar e recuperar do cache"""
        key = "12345678000190"
        data = {"cnpj": key, "corporate_name": "Teste"}
        
        receita_scraper._save_to_cache(key, data)
        cached = receita_scraper._get_from_cache(key)
        
        assert cached == data
    
    def test_cache_expiration(self, receita_scraper):
        """Testa expiração do cache"""
        key = "12345678000190"
        data = {"cnpj": key}
        
        # Salvar com TTL muito curto
        receita_scraper.cache_ttl = timedelta(seconds=-1)
        receita_scraper._save_to_cache(key, data)
        
        cached = receita_scraper._get_from_cache(key)
        
        assert cached is None
    
    def test_clear_cache(self, receita_scraper):
        """Testa limpeza do cache"""
        receita_scraper._save_to_cache("key1", {"a": 1})
        receita_scraper._save_to_cache("key2", {"b": 2})
        
        assert len(receita_scraper.cache) == 2
        
        receita_scraper.clear_cache()
        
        assert len(receita_scraper.cache) == 0
    
    def test_get_cache_stats(self):
        """Testa estatísticas do cache"""
        scraper = ReceitaScraper()
        
        # Cache válido
        scraper._save_to_cache("valid1", {"a": 1})
        scraper._save_to_cache("valid2", {"b": 2})
        
        # Forçar cache expirado
        scraper.cache["expired"] = (datetime.now() - timedelta(hours=49), {"c": 3})
        
        stats = scraper.get_cache_stats()
        
        assert stats["total_entries"] == 3
        assert stats["valid_entries"] == 2
        assert stats["expired_entries"] == 1
        assert stats["ttl_hours"] == 48


class TestReceitaScraperSecondaryActivities:
    """Testes para atividades secundárias"""
    
    def test_extract_secondary_activities(self, receita_scraper, mock_company_data_brasilapi):
        """Testa extração de CNAEs secundários"""
        activities = receita_scraper._extract_secondary_activities(mock_company_data_brasilapi)
        
        assert len(activities) == 1
        assert activities[0]["code"] == "6202300"
        assert "programas de computador" in activities[0]["description"].lower()
    
    def test_extract_secondary_activities_empty(self, receita_scraper):
        """Testa extração sem CNAEs secundários"""
        data = {"cnaes_secundarios": []}
        activities = receita_scraper._extract_secondary_activities(data)
        
        assert activities == []


class TestReceitaScraperFilialIdentification:
    """Testes para identificação de filiais"""
    
    def test_extract_related_cnpjs_for_filial(self, receita_scraper):
        """Testa extração de matriz quando é filial"""
        data = {
            "cnpj": "12345678000290",  # Filial (não é 0001)
            "identificador_matriz_filial": "2",  # É filial
        }
        partners = []
        
        related = receita_scraper._extract_related_cnpjs(data, partners)
        
        # Deve identificar matriz
        matriz = [r for r in related if r["relationship"] == "Matriz"]
        assert len(matriz) == 1
        assert "12345678" in matriz[0]["cnpj_clean"]  # Primeiros 8 dígitos iguais
