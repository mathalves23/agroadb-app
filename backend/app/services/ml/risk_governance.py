"""
Governança e transparência do score de risco (LGPD / ANPD — explicabilidade, RIPD).
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.organization import OrganizationRepository

logger = logging.getLogger(__name__)

METHODOLOGY_PT = (
    "O score é produzido por regras interpretáveis: cada indicador numérico (0–100) é multiplicado "
    "por um peso fixo documentado na API; a soma ponderada é o score bruto. Opcionalmente aplica-se "
    "uma transformação monótona de calibração (ficheiro JSON versionado por impressão digital). "
    "É fornecida uma decomposição aditiva tipo SHAP sobre um baseline neutro, para aproximar a "
    "contribuição marginal de cada indicador ao score bruto. Este output não substitui parecer "
    "humano nem decisão de crédito."
)


def calibration_fingerprint(cfg: Dict[str, Any]) -> str:
    try:
        blob = json.dumps(cfg, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:16]
    except Exception as exc:  # pragma: no cover - defensivo
        logger.debug("Fingerprint de calibração indisponível: %s", exc)
        return "unavailable"


async def primary_org_risk_policy(
    db: AsyncSession, owner_user_id: int
) -> Tuple[Optional[int], bool, Optional[str]]:
    """
    Política da primeira organização do dono da investigação (alinhado a saas_enforcement).
    """
    orgs = await OrganizationRepository(db).list_for_user(owner_user_id)
    if not orgs:
        return None, False, None
    org = orgs[0]
    required = bool(getattr(org, "risk_ai_human_review_required", False))
    ref = getattr(org, "risk_ai_governance_reference_url", None)
    return org.id, required, ref


async def build_risk_governance_context(
    db: AsyncSession,
    *,
    owner_user_id: int,
    indicator_weights: Dict[str, float],
    calibration_config: Dict[str, Any],
    calibration_meta: Dict[str, Any],
) -> Dict[str, Any]:
    org_id, human_required, gov_ref = await primary_org_risk_policy(db, owner_user_id)
    cal_path = (settings.RISK_CALIBRATION_PATH or "").strip()
    fp = calibration_fingerprint(calibration_config)

    return {
        "engine_version": settings.RISK_ENGINE_VERSION,
        "weights_version": settings.RISK_WEIGHTS_VERSION,
        "indicator_weights": dict(indicator_weights),
        "methodology_summary_pt": METHODOLOGY_PT,
        "calibration": {
            **calibration_meta,
            "config_fingerprint_sha256_16": fp,
            "config_source": "explicit_env_path" if cal_path else "bundled_default",
            "config_path_set": bool(cal_path),
        },
        "app_release_version": settings.VERSION,
        "human_review_required": human_required,
        "human_review_basis": (
            "Política da organização (revisão humana obrigatória antes de efeitos decisórios)."
            if human_required
            else None
        ),
        "organization_id": org_id,
        "governance_reference_url": gov_ref,
        "legal_notice_pt": (
            "Tratamento baseado em legítimo interesse ou execução de contrato B2B; dados agregados "
            "de fontes públicas. Consulte o RIPD/DPIA da sua organização e o registo de tratamentos."
        ),
    }
