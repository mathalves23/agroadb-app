"""
Testes para o SIGEF/SICAR Scraper

Cobre:
- Busca de imóveis certificados
- Download de shapefiles
- Busca por coordenadas
- Cálculo de área
- Verificação de sobreposição
- Conversão de datum
- Cache
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from app.scrapers.sigef_sicar_scraper import SIGEFSICARScraper


@pytest.fixture
def sigef_scraper():
    return SIGEFSICARScraper()


@pytest.mark.asyncio
async def test_search_sigef(sigef_scraper):
    """Testa busca de imóveis SIGEF"""
    results = await sigef_scraper.search_sigef(
        codigo_imovel="SIGEF-001-2024",
        uf="SP"
    )
    
    assert len(results) > 0
    assert "codigo_imovel" in results[0]
    assert "geometry" in results[0]


@pytest.mark.asyncio
async def test_search_sigef_by_municipio(sigef_scraper):
    """Testa busca por município"""
    results = await sigef_scraper.search_sigef(
        municipio="São Paulo",
        uf="SP"
    )
    
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_download_shapefile(sigef_scraper):
    """Testa download de shapefile"""
    with patch.object(sigef_scraper, 'search_sigef', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{
            "codigo_imovel": "SIGEF-001",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-47.1, -22.9], [-47.0, -22.9], [-47.1, -22.9]]]
            }
        }]
        
        result = await sigef_scraper.download_shapefile("SIGEF-001", "geojson")
        
        assert result is not None
        assert result["format"] == "geojson"
        assert "download_url" in result


@pytest.mark.asyncio
async def test_search_by_coordinates(sigef_scraper):
    """Testa busca por coordenadas"""
    results = await sigef_scraper.search_by_coordinates(
        latitude=-22.9,
        longitude=-47.1,
        radius_km=5.0
    )
    
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_calculate_area(sigef_scraper):
    """Testa cálculo de área"""
    geometry = {
        "type": "Polygon",
        "coordinates": [[
            [-47.1, -22.9],
            [-47.0, -22.9],
            [-47.0, -22.8],
            [-47.1, -22.8],
            [-47.1, -22.9],
        ]]
    }
    
    result = await sigef_scraper.calculate_area(geometry)
    
    assert "area_ha" in result
    assert "area_m2" in result
    assert "perimetro_m" in result


@pytest.mark.asyncio
async def test_verify_overlap(sigef_scraper):
    """Testa verificação de sobreposição"""
    geometry1 = {"type": "Polygon", "coordinates": [[[-47.1, -22.9]]]}
    geometry2 = {"type": "Polygon", "coordinates": [[[-47.2, -23.0]]]}
    
    result = await sigef_scraper.verify_overlap(geometry1, geometry2)
    
    assert "has_overlap" in result
    assert "overlap_area_ha" in result


@pytest.mark.asyncio
async def test_convert_datum(sigef_scraper):
    """Testa conversão de datum"""
    coords = [(-47.1, -22.9), (-47.0, -22.8)]
    
    result = await sigef_scraper.convert_datum(
        coords,
        from_datum="SIRGAS2000",
        to_datum="WGS84"
    )
    
    assert len(result) == len(coords)
    assert isinstance(result, list)


def test_get_supported_formats(sigef_scraper):
    """Testa obtenção de formatos suportados"""
    formats = sigef_scraper.get_supported_formats()
    
    assert "geojson" in formats
    assert "kmz" in formats
    assert "shapefile" in formats


def test_cache(sigef_scraper):
    """Testa sistema de cache"""
    key = "test_key"
    data = [{"codigo_imovel": "SIGEF-001"}]
    
    sigef_scraper._save_to_cache(key, data)
    cached = sigef_scraper._get_from_cache(key)
    
    assert cached == data


def test_clear_cache(sigef_scraper):
    """Testa limpeza do cache"""
    sigef_scraper._save_to_cache("key1", [{"a": 1}])
    assert len(sigef_scraper.cache) >= 1
    
    sigef_scraper.clear_cache()
    assert len(sigef_scraper.cache) == 0


def test_cache_stats(sigef_scraper):
    """Testa estatísticas do cache"""
    sigef_scraper.clear_cache()
    sigef_scraper._save_to_cache("key1", [{"a": 1}])
    
    stats = sigef_scraper.get_cache_stats()
    
    assert stats["total_entries"] >= 1
    assert stats["valid_entries"] >= 1
    assert stats["ttl_hours"] == 24
