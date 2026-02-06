"""
Scrapers - complementam as APIs para enriquecer a base de dados.

Cada scraper pode ser usado quando a API correspondente não está configurada
ou para obter dados adicionais via páginas públicas (HTML) ou fontes abertas.

Scrapers disponíveis:
- TribunaisScraper: ESAJ, Projudi, PJe (processos judiciais)
- CARPublicScraper: CAR/SICAR (consulta pública)
- SNCRPublicScraper: SNCR/CCIR (cadastro rural)
- SigefParcelasScraper: SIGEF (parcelas certificadas, ArcGIS)
- ReceitaScraper: CNPJ (APIs + fallback HTML)
- CARScraper, INCRAScraper, SIGEFSICARScraper, etc. (existentes)
"""
from app.scrapers.base import BaseScraper
from app.scrapers.tribunais_scraper import TribunaisScraper
from app.scrapers.car_public_scraper import CARPublicScraper
from app.scrapers.sncr_public_scraper import SNCRPublicScraper
from app.scrapers.sigef_parcelas_scraper import SigefParcelasScraper
from app.scrapers.car_scraper import CARScraper
from app.scrapers.incra_scraper import INCRAScraper
from app.scrapers.receita_scraper import ReceitaScraper
from app.scrapers.sigef_sicar_scraper import SIGEFSICARScraper

__all__ = [
    "BaseScraper",
    "TribunaisScraper",
    "CARPublicScraper",
    "SNCRPublicScraper",
    "SigefParcelasScraper",
    "CARScraper",
    "INCRAScraper",
    "ReceitaScraper",
    "SIGEFSICARScraper",
]

# Scrapers que complementam as integrações legais/governamentais (para workers/fila)
SCRAPERS_LEGAL_GOV = [
    TribunaisScraper,
    CARPublicScraper,
    SNCRPublicScraper,
    SigefParcelasScraper,
]
