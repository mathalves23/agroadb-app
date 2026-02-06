"""
Integrações Externas - AgroADB

Este módulo contém todas as integrações com sistemas externos:
- CAR de todos os 27 estados brasileiros
- Tribunais estaduais (ESAJ, Projudi)
- Órgãos federais (IBAMA, FUNAI, ICMBio, SPU)
- Bureaus de crédito (Serasa, Boa Vista)
- Ferramentas de comunicação (Slack, Microsoft Teams)
"""

from app.integrations.car_estados import CARIntegration
from app.integrations.tribunais import TribunalIntegration
from app.integrations.orgaos_federais import OrgaoFederalIntegration
from app.integrations.bureaus import BureauIntegration
from app.integrations.comunicacao import ComunicacaoIntegration

__all__ = [
    "CARIntegration",
    "TribunalIntegration",
    "OrgaoFederalIntegration",
    "BureauIntegration",
    "ComunicacaoIntegration",
]
