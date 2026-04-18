#!/usr/bin/env python3
"""
Gera o pacote app/api/v1/endpoints/integrations/ a partir de integrations.py.
Executar na raiz do repositório: python3 backend/scripts/split_integrations_router.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENDPOINTS = ROOT / "app" / "api" / "v1" / "endpoints"
SRC = ENDPOINTS / "integrations.py"
PKG = ENDPOINTS / "integrations"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Falta {SRC}")
    lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)

    def sl(lo: int, hi: int) -> str:
        return "".join(lines[lo - 1 : hi])

    header = sl(1, 62)
    schemas_block = sl(185, 315)

    conecta = (
        '"""Sub-router Conecta gov.br + SIGEF parcelas (WS)."""\n'
        + header
        + "router = APIRouter()\n\n"
        + schemas_block
        + "\n"
        + sl(317, 1139)
    )

    tribunais = (
        '"""Sub-router tribunais (consulta simples, e-SAJ, Projudi)."""\n'
        + header
        + "router = APIRouter()\n\n"
        + schemas_block
        + "\n"
        + sl(2639, 2647)
        + sl(2649, 2849)
    )

    biros = (
        '"""Sub-router órgãos federais, birôs e notificações (Slack/Teams)."""\n'
        + header
        + "router = APIRouter()\n\n"
        + schemas_block
        + "\n"
        + sl(1197, 1393)
    )

    # Remainder = ficheiro completo sem blocos movidos para sub-routers
    remove_idx: set[int] = set()
    remove_idx.update(range(316, 1140))  # linhas 317–1140 (Conecta + SIGEF inicial)
    remove_idx.update(range(1169, 1195))  # 1170–1195 tribunais simples
    remove_idx.update(range(1196, 1393))  # 1197–1393 órgãos / birôs / notify
    remove_idx.update(range(2648, 2849))  # 2649–2849 e-SAJ / Projudi (até antes de Birôs de Crédito)
    remainder_lines = [ln for i, ln in enumerate(lines) if i not in remove_idx]
    remainder_text = "".join(remainder_lines)
    remainder_text = remainder_text.replace(
        'router = APIRouter(prefix="/integrations", tags=["integrations"])',
        'router = APIRouter()',
        1,
    )
    remainder = (
        '"""Integrações: status, CAR, APIs públicas, transparência, IBAMA, etc."""\n'
        + remainder_text
    )

    if PKG.exists():
        shutil.rmtree(PKG)
    PKG.mkdir(parents=True)

    (PKG / "conecta.py").write_text(conecta, encoding="utf-8")
    (PKG / "tribunais.py").write_text(tribunais, encoding="utf-8")
    (PKG / "biros_orgaos_notify.py").write_text(biros, encoding="utf-8")
    (PKG / "remainder.py").write_text(remainder, encoding="utf-8")
    import subprocess
    import sys

    split_script = ROOT / "scripts" / "split_remainder_routers.py"
    if split_script.exists():
        subprocess.run(
            [sys.executable, str(split_script)],
            cwd=str(ROOT),
            check=True,
        )
        (PKG / "remainder.py").unlink(missing_ok=True)

    init = '''"""Pacote de routers de integrações externas (sub-routers + restante)."""
from fastapi import APIRouter

from .biros_orgaos_notify import router as biros_router
from .conecta import router as conecta_router
from .remainder_environment import router as remainder_environment_router
from .remainder_open_data import router as remainder_open_data_router
from .remainder_supervision import router as remainder_supervision_router
from .remainder_transparency import router as remainder_transparency_router
from .tribunais import router as tribunais_router

router = APIRouter(prefix="/integrations", tags=["integrations"])
router.include_router(remainder_open_data_router)
router.include_router(remainder_transparency_router)
router.include_router(remainder_supervision_router)
router.include_router(remainder_environment_router)
router.include_router(conecta_router)
router.include_router(tribunais_router)
router.include_router(biros_router)
'''
    (PKG / "__init__.py").write_text(init, encoding="utf-8")

    backup = ENDPOINTS / "integrations_monolith_pre_split.py.bak"
    shutil.copy2(SRC, backup)
    SRC.unlink()
    print(f"OK: {PKG} criado; backup: {backup}")


if __name__ == "__main__":
    main()
