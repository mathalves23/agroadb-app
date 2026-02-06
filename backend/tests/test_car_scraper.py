"""
Testes para o CAR Scraper

Cobre:
- Busca por CPF/CNPJ
- Busca por nome
- Busca por número do CAR
- Busca por município
- Cache de resultados
- Parsing de coordenadas geográficas
- Cálculo de centroide
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.scrapers.car_scraper import CARScraper


@pytest.fixture
def car_scraper():
    """Fixture que retorna uma instância do CARScraper"""
    return CARScraper()


@pytest.fixture
def mock_car_demonstrativo_data():
    """Dados mockados da API do demonstrativo CAR"""
    return {
        "nomeImovel": "Fazenda Teste",
        "proprietario": "João Silva",
        "cpfCnpj": "12345678000190",
        "estado": "SP",
        "municipio": "Campinas",
        "areaApp": 10.5,
        "areaReservaLegal": 50.0,
        "areaConsolidada": 100.0,
        "dataInscricao": "2020-01-15",
        "dataAtualizacao": "2024-06-20",
        "bioma": "Mata Atlântica",
        "baciaHidrografica": "Rio Piracicaba",
        "terraIndigena": False,
        "unidadeConservacao": False,
    }


@pytest.fixture
def mock_car_imovel_data():
    """Dados mockados da API do imóvel CAR"""
    return {
        "nomePropriedade": "Fazenda Teste",
        "nomeProprietario": "João Silva",
        "cpfCnpjProprietario": "12345678000190",
        "uf": "SP",
        "municipio": "Campinas",
        "endereco": "Zona Rural, s/n",
        "areaImovel": 160.5,
        "status": "Ativo",
        "latitude": -22.9,
        "longitude": -47.1,
        "geometria": {
            "type": "Polygon",
            "coordinates": [[
                [-47.1, -22.9],
                [-47.0, -22.9],
                [-47.0, -22.8],
                [-47.1, -22.8],
                [-47.1, -22.9],
            ]]
        }
    }


class TestCARScraperSearch:
    """Testes para o método search"""
    
    @pytest.mark.asyncio
    async def test_search_by_cpf_cnpj(self, car_scraper):
        """Testa busca por CPF/CNPJ"""
        with patch.object(car_scraper, '_search_by_cpf_cnpj', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [{
                "car_number": "SP-1234567-ABC",
                "owner_cpf_cnpj": "12345678000190",
            }]
            
            results = await car_scraper.search(cpf_cnpj="123.456.780/0001-90")
            
            assert len(results) == 1
            assert results[0]["car_number"] == "SP-1234567-ABC"
            mock_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_by_name_fallback(self, car_scraper):
        """Testa busca por nome quando CPF/CNPJ não retorna resultados"""
        with patch.object(car_scraper, '_search_by_cpf_cnpj', new_callable=AsyncMock) as mock_cpf, \
             patch.object(car_scraper, '_search_by_name', new_callable=AsyncMock) as mock_name:
            
            mock_cpf.return_value = []
            mock_name.return_value = [{
                "property_name": "Fazenda Teste",
                "owner_name": "João Silva",
            }]
            
            results = await car_scraper.search(
                name="João Silva",
                cpf_cnpj="12345678000190"
            )
            
            # Deve tentar buscar por nome quando CPF não retorna resultados
            mock_name.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_with_cache(self, car_scraper):
        """Testa que resultados são retornados do cache"""
        # Adicionar ao cache manualmente
        cache_key = "João Silva_None_SP_None"
        cached_data = [{"property_name": "Fazenda Teste"}]
        car_scraper._save_to_cache(cache_key, cached_data)
        
        # Buscar deve retornar do cache
        results = await car_scraper.search(name="João Silva", state="SP")
        
        assert results == cached_data
    
    @pytest.mark.asyncio
    async def test_search_handles_errors_gracefully(self, car_scraper):
        """Testa que erros não quebram a busca"""
        with patch.object(car_scraper, '_search_by_cpf_cnpj', side_effect=Exception("API Error")):
            results = await car_scraper.search(cpf_cnpj="12345678000190")
            
            # Deve retornar lista vazia em caso de erro
            assert results == []


class TestCARScraperCPFCNPJSearch:
    """Testes para busca por CPF/CNPJ"""
    
    @pytest.mark.asyncio
    async def test_search_by_cpf_cnpj_cleans_input(self, car_scraper):
        """Testa que CPF/CNPJ é limpo corretamente"""
        results = await car_scraper._search_by_cpf_cnpj("123.456.780/0001-90", "SP")
        
        assert len(results) == 1
        # CPF/CNPJ deve estar limpo (sem pontuação)
        assert results[0]["owner_cpf_cnpj"] == "123456780000190"
    
    @pytest.mark.asyncio
    async def test_search_by_cpf_cnpj_structure(self, car_scraper):
        """Testa estrutura de dados retornada"""
        results = await car_scraper._search_by_cpf_cnpj("12345678000190", "SP")
        
        assert len(results) == 1
        result = results[0]
        
        # Verificar campos obrigatórios
        assert "car_number" in result
        assert "property_name" in result
        assert "owner_name" in result
        assert "owner_cpf_cnpj" in result
        assert "state" in result
        assert "city" in result
        assert "area_total_hectares" in result
        assert "coordinates" in result
        assert "centroid" in result
        assert "status" in result
        assert "data_source" in result
        assert result["data_source"] == "CAR/SICAR"


class TestCARScraperGetPropertyByNumber:
    """Testes para busca por número do CAR"""
    
    @pytest.mark.asyncio
    async def test_get_property_by_car_number_from_cache(
        self, car_scraper, mock_car_demonstrativo_data
    ):
        """Testa retorno do cache"""
        car_number = "SP-1234567-ABC"
        cached_data = [{
            "car_number": car_number,
            "property_name": "Fazenda Teste",
        }]
        car_scraper._save_to_cache(f"car_{car_number}", cached_data)
        
        result = await car_scraper.get_property_by_car_number(car_number)
        
        assert result is not None
        assert result["car_number"] == car_number
    
    @pytest.mark.asyncio
    async def test_get_property_by_car_number_api_call(
        self, car_scraper, mock_car_demonstrativo_data, mock_car_imovel_data
    ):
        """Testa chamada à API quando não está no cache"""
        car_number = "SP-1234567-ABC"
        
        # Mock das respostas da API
        mock_demo_response = Mock()
        mock_demo_response.json.return_value = mock_car_demonstrativo_data
        
        mock_imovel_response = Mock()
        mock_imovel_response.json.return_value = mock_car_imovel_data
        
        with patch.object(car_scraper, 'fetch', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = [mock_demo_response, mock_imovel_response]
            
            result = await car_scraper.get_property_by_car_number(car_number)
            
            assert result is not None
            assert result["car_number"] == car_number
            assert result["property_name"] == "Fazenda Teste"
            assert result["owner_name"] == "João Silva"
            assert result["state"] == "SP"
            assert result["city"] == "Campinas"
            
            # Verificar que fetch foi chamado 2 vezes (demonstrativo + imóvel)
            assert mock_fetch.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_property_by_car_number_not_found(self, car_scraper):
        """Testa quando propriedade não é encontrada"""
        car_number = "INVALID-CAR-NUMBER"
        
        with patch.object(car_scraper, 'fetch', new_callable=AsyncMock, return_value=None):
            result = await car_scraper.get_property_by_car_number(car_number)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_property_by_car_number_handles_errors(self, car_scraper):
        """Testa tratamento de erros"""
        car_number = "SP-1234567-ABC"
        
        with patch.object(car_scraper, 'fetch', side_effect=Exception("Network Error")):
            result = await car_scraper.get_property_by_car_number(car_number)
            
            assert result is None


class TestCARScraperParseData:
    """Testes para parsing de dados"""
    
    def test_parse_car_data_complete(
        self, car_scraper, mock_car_demonstrativo_data, mock_car_imovel_data
    ):
        """Testa parsing com dados completos"""
        car_number = "SP-1234567-ABC"
        
        result = car_scraper._parse_car_data(
            mock_car_demonstrativo_data,
            mock_car_imovel_data,
            car_number
        )
        
        assert result["car_number"] == car_number
        assert result["property_name"] == "Fazenda Teste"
        assert result["owner_name"] == "João Silva"
        assert result["owner_cpf_cnpj"] == "12345678000190"
        assert result["state"] == "SP"
        assert result["city"] == "Campinas"
        assert result["area_total_hectares"] == 160.5
        assert result["area_app_hectares"] == 10.5
        assert result["area_reserva_legal_hectares"] == 50.0
        assert result["biome"] == "Mata Atlântica"
        assert result["indigenous_land"] is False
    
    def test_parse_car_data_missing_fields(self, car_scraper):
        """Testa parsing com campos faltando"""
        car_number = "SP-1234567-ABC"
        demonstrativo = {"nomeImovel": "Fazenda"}
        imovel = {}
        
        result = car_scraper._parse_car_data(demonstrativo, imovel, car_number)
        
        # Deve ter valores padrão para campos faltando
        assert result["area_total_hectares"] == 0.0
        assert result["area_app_hectares"] == 0.0
        assert result["status"] == "Desconhecido"


class TestCARScraperCoordinates:
    """Testes para extração e cálculo de coordenadas"""
    
    def test_extract_coordinates_polygon(self, car_scraper):
        """Testa extração de coordenadas em formato Polygon"""
        imovel_data = {
            "geometria": {
                "type": "Polygon",
                "coordinates": [[
                    [-47.1, -22.9],
                    [-47.0, -22.9],
                    [-47.0, -22.8],
                    [-47.1, -22.8],
                    [-47.1, -22.9],
                ]]
            }
        }
        
        result = car_scraper._extract_coordinates(imovel_data)
        
        assert result["polygon"]["type"] == "Polygon"
        assert len(result["polygon"]["coordinates"]) > 0
        assert result["centroid"]["latitude"] != 0
        assert result["centroid"]["longitude"] != 0
    
    def test_extract_coordinates_multipolygon(self, car_scraper):
        """Testa extração de coordenadas em formato MultiPolygon"""
        imovel_data = {
            "geometria": {
                "type": "MultiPolygon",
                "coordinates": [
                    [[
                        [-47.1, -22.9],
                        [-47.0, -22.9],
                        [-47.0, -22.8],
                        [-47.1, -22.8],
                        [-47.1, -22.9],
                    ]]
                ]
            }
        }
        
        result = car_scraper._extract_coordinates(imovel_data)
        
        # Deve converter para Polygon (primeiro polígono)
        assert result["polygon"]["type"] == "Polygon"
        assert len(result["polygon"]["coordinates"]) > 0
    
    def test_extract_coordinates_fallback_to_centroid(self, car_scraper):
        """Testa fallback para coordenadas de centroide"""
        imovel_data = {
            "latitude": -22.9,
            "longitude": -47.1,
        }
        
        result = car_scraper._extract_coordinates(imovel_data)
        
        assert result["centroid"]["latitude"] == -22.9
        assert result["centroid"]["longitude"] == -47.1
    
    def test_extract_coordinates_empty(self, car_scraper):
        """Testa extração com dados vazios"""
        imovel_data = {}
        
        result = car_scraper._extract_coordinates(imovel_data)
        
        assert result["polygon"]["type"] == "Polygon"
        assert result["polygon"]["coordinates"] == []
        assert result["centroid"]["latitude"] == 0.0
        assert result["centroid"]["longitude"] == 0.0
    
    def test_calculate_centroid(self, car_scraper):
        """Testa cálculo do centroide"""
        coords = [
            [-47.1, -22.9],
            [-47.0, -22.9],
            [-47.0, -22.8],
            [-47.1, -22.8],
            [-47.1, -22.9],
        ]
        
        centroid = car_scraper._calculate_centroid(coords)
        
        # Média das coordenadas
        assert centroid["latitude"] == pytest.approx(-22.86, rel=0.01)
        assert centroid["longitude"] == pytest.approx(-47.06, rel=0.01)
    
    def test_calculate_centroid_empty(self, car_scraper):
        """Testa cálculo de centroide com lista vazia"""
        centroid = car_scraper._calculate_centroid([])
        
        assert centroid["latitude"] == 0.0
        assert centroid["longitude"] == 0.0


class TestCARScraperCache:
    """Testes para sistema de cache"""
    
    def test_save_and_get_from_cache(self, car_scraper):
        """Testa salvar e recuperar do cache"""
        key = "test_key"
        data = [{"property": "test"}]
        
        car_scraper._save_to_cache(key, data)
        cached = car_scraper._get_from_cache(key)
        
        assert cached == data
    
    def test_cache_expiration(self, car_scraper):
        """Testa expiração do cache"""
        key = "test_key"
        data = [{"property": "test"}]
        
        # Salvar com TTL muito curto
        car_scraper.cache_ttl = timedelta(seconds=-1)  # Já expirado
        car_scraper._save_to_cache(key, data)
        
        cached = car_scraper._get_from_cache(key)
        
        assert cached is None
    
    def test_clear_cache(self, car_scraper):
        """Testa limpeza do cache"""
        car_scraper._save_to_cache("key1", [{"a": 1}])
        car_scraper._save_to_cache("key2", [{"b": 2}])
        
        assert len(car_scraper.cache) == 2
        
        car_scraper.clear_cache()
        
        assert len(car_scraper.cache) == 0
    
    def test_get_cache_stats(self):
        """Testa estatísticas do cache"""
        # Criar nova instância para garantir cache limpo
        scraper = CARScraper()
        
        # Cache válido
        scraper._save_to_cache("valid1", [{"a": 1}])
        scraper._save_to_cache("valid2", [{"b": 2}])
        
        # Forçar um cache expirado manualmente inserindo no dicionário
        from datetime import datetime, timedelta
        scraper.cache["expired"] = (datetime.now() - timedelta(hours=25), [{"c": 3}])
        
        stats = scraper.get_cache_stats()
        
        assert stats["total_entries"] == 3
        assert stats["valid_entries"] == 2
        assert stats["expired_entries"] == 1
        assert stats["ttl_hours"] == 24


class TestCARScraperSearchByMunicipality:
    """Testes para busca por município"""
    
    @pytest.mark.asyncio
    async def test_search_by_municipality(self, car_scraper):
        """Testa busca por município"""
        results = await car_scraper.search_by_municipality("SP", "Campinas", limit=50)
        
        # Por enquanto retorna vazio (TODO implementar)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_by_municipality_handles_errors(self, car_scraper):
        """Testa tratamento de erros na busca por município"""
        with patch.object(car_scraper, 'fetch', side_effect=Exception("API Error")):
            results = await car_scraper.search_by_municipality("SP", "Invalid")
            
            assert results == []
