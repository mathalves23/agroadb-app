"""
Funções partilhadas dos endpoints de integrações (bounded context: Integrações externas).

Mantidas fora dos routers em `integrations/` para reduzir dívida técnica e
permitir testes unitários isolados.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def result_count(result: Any) -> int:
    if isinstance(result, list):
        return len(result)
    if isinstance(result, dict):
        for key in ("parcelas", "resultados", "itens", "items", "processos", "hits"):
            value = result.get(key)
            if isinstance(value, list):
                return len(value)
    return 0


def is_credentials_missing(exc: Exception) -> bool:
    msg = str(exc).lower()
    return (
        "não configuradas" in msg or "credenciais conecta" in msg or "credenciais ausentes" in msg
    )


def conecta_items(result: Any) -> list:
    """Extrai lista de itens do resultado para resposta padronizada."""
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("items", "itens", "resultados", "parcelas", "hits", "data"):
            value = result.get(key)
            if isinstance(value, list):
                return value
        return [result]
    return [result] if result is not None else []


def conecta_standard_response(
    result: Any,
    pagination: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Resposta padronizada para endpoints Conecta: success, items, pagination, warnings."""
    return {
        "success": True,
        "items": conecta_items(result),
        "data": result,
        "pagination": pagination or {},
        "warnings": warnings or [],
    }
