#!/usr/bin/env python3
"""One-shot: parte remainder.py em routers por domínio (não executar de CI)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "app/api/v1/endpoints/integrations/remainder.py"
OUT = ROOT / "app/api/v1/endpoints/integrations"

COMMON_IMPORTS = """from fastapi import APIRouter, Depends, HTTPException, status, Query
import io
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict
import logging

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.deps import get_current_user
from app.domain.user import User
from app.integrations.car_estados import CARIntegration, query_car_single
from app.integrations.tribunais import TribunalIntegration, query_process_by_number
from app.integrations.orgaos_federais import OrgaoFederalIntegration
from app.integrations.bureaus import BureauIntegration
from app.integrations.comunicacao import ComunicacaoIntegration
from app.services.sigef_parcelas import SigefParcelasService
from app.services.conecta_sncr import ConectaSNCRService
from app.services.conecta_sigef import ConectaSIGEFService
from app.services.conecta_sicar import ConectaSICARService
from app.services.conecta_sncci import ConectaSNCCIService
from app.services.conecta_sigef_geo import ConectaSIGEFGeoService
from app.services.conecta_cnpj import ConectaCNPJService
from app.services.conecta_cnd import ConectaCNDService
from app.services.conecta_cadin import ConectaCadinService
from app.services.portal_servicos import PortalServicosService
from app.services.servicos_estaduais import ServicosEstaduaisService
from app.services.brasil_api import BrasilAPIService
from app.services.portal_transparencia import PortalTransparenciaService
from app.services.ibge_api import IBGEService
from app.services.tse_api import TSEService
from app.services.cvm_api import CVMService
from app.services.bcb_api import BCBService
from app.services.dados_gov import DadosGovService
from app.services.redesim_api import RedesimService
from app.services.tjmg_api import TJMGService
from app.services.antecedentes_mg import AntecedentesMGService
from app.services.sicar_publico import SICARPublicoService
from app.services.caixa_fgts import CaixaFGTSService
from app.services.bnmp_cnj import BNMPService
from app.services.seeu_cnj import SEEUService
from app.services.sigef_publico import SIGEFPublicoService
from app.services.receita_cpf import ReceitaCPFService
from app.services.receita_cnpj import ReceitaCNPJService
from app.repositories.legal_query import LegalQueryRepository
from app.core.audit import AuditLogger
from app.api.v1.endpoints.integrations_helpers import (
    result_count as _result_count,
    is_credentials_missing as _is_credentials_missing,
    conecta_items as _conecta_items,
    conecta_standard_response as _conecta_standard_response,
)

logger = logging.getLogger(__name__)
audit_logger = AuditLogger()

router = APIRouter()
"""

SPECS = [
    (
        "remainder_open_data.py",
        "Integrações — dados abertos, status, CAR, Conecta, SIGEF, birôs e health.",
        # Exclui linha `router = APIRouter()` do monólito (já em COMMON_IMPORTS).
        [(66, 437), (2348, 2383)],
    ),
    (
        "remainder_transparency.py",
        "Integrações — transparência federal, REDESIM, IBGE, TSE, CVM, BCB, dados.gov.",
        [(439, 987)],
    ),
    (
        "remainder_supervision.py",
        "Integrações — tribunais estaduais, fiscalização cadastral, birôs de crédito, órgãos.",
        [(989, 1897)],
    ),
    (
        "remainder_environment.py",
        "Integrações — IBAMA, FUNAI, ICMBio (fiscalização ambiental).",
        [(1899, 2346)],
    ),
]


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    for filename, doc, ranges in SPECS:
        parts: list[str] = []
        for start_1, end_1 in ranges:
            parts.extend(lines[start_1 - 1 : end_1])
        body = "".join(parts)
        content = f'"""{doc}"""\n\n{COMMON_IMPORTS}\n{body}'
        (OUT / filename).write_text(content, encoding="utf-8")
        print("wrote", filename, "lines", len(content.splitlines()))


if __name__ == "__main__":
    main()
