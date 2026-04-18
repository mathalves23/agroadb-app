"""Proposta de valor e pilares de conformidade (fonte única para API e documentação)."""
from __future__ import annotations

from typing import Any, Dict, List

from app.core.config import settings


def build_value_proposition() -> Dict[str, Any]:
    return {
        "product": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "primary_segments": [
            {
                "id": "law_agribusiness",
                "label": "Escritórios de advocacia — agronegócio e crédito rural",
                "value": "Due diligence patrimonial, defesa em conflitos fundiários e análise de garantias com dados integrados.",
            },
            {
                "id": "rural_credit",
                "label": "Bancos e cooperativas — crédito rural",
                "value": "Enriquecimento de cadastro, visão de imóveis SIGEF/SNCR/SICAR e risco reputacional/legal.",
            },
        ],
        "differentiators": [
            {
                "title": "Conformidade LGPD",
                "points": [
                    "Módulos LGPD e exportação de dados sujeitos a direitos do titular (quando aplicável).",
                    "Minimização de dados: integrações configuráveis e trilhos de auditoria nas acções sensíveis.",
                ],
            },
            {
                "title": "Trilhos de auditoria",
                "points": [
                    "Registo de operações em investigações (criação, alteração, eliminação).",
                    "Integrações legais e consultas externas com registo em repositório de consultas.",
                ],
            },
            {
                "title": "Relatórios exportáveis",
                "points": [
                    "PDF e Excel de investigações na API de exportação.",
                    "Export de grafos (JSON / GraphML) para análise externa e pareceres.",
                ],
            },
        ],
        "api_public_surfaces": [
            "/api/v1/investigations",
            "/api/v1/legal",
            "/api/v1/integrations",
            "/api/v1/lgpd",
            "/api/v1/security",
        ],
        "documentation_links": {
            "bounded_contexts": "/docs/bounded-contexts/README.md (repositório)",
            "deploy_docker": "/docs/deploy/primeiro-deploy-docker.md",
            "deploy_k8s": "/docs/deploy/primeiro-deploy-kubernetes.md",
        },
    }


def build_compliance_summary() -> Dict[str, Any]:
    pillars: List[Dict[str, str]] = [
        {"id": "lgpd", "name": "LGPD", "status": "supported", "note": "Endpoints dedicados em /api/v1/lgpd"},
        {"id": "audit", "name": "Auditoria", "status": "supported", "note": "AuditLogger em fluxos de investigação e integrações legais"},
        {"id": "exports", "name": "Exportação", "status": "supported", "note": "PDF, Excel, grafo JSON/GraphML"},
    ]
    return {
        "pillars": pillars,
        "environment": settings.ENVIRONMENT,
        "message": "Use estes pilares em materiais comerciais e RFPs; detalhe técnico na documentação do repositório.",
    }
