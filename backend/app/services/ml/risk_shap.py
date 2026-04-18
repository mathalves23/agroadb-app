"""
Explicabilidade tipo SHAP para o score de risco.

O motor actual é **aditivo e linear nos indicadores**:
``total_raw = sum_i w_i * v_i`` com ``v_i`` em [0, 100].

Para este caso, os valores de Shapley com baseline fixa ``b`` coincidem com
``phi_i = w_i * (v_i - b_i)`` e ``sum_i phi_i = f(v) - f(b)`` (modelo aditivo).

Referência: Lundberg & Lee, *A Unified Approach to Interpreting Model Predictions*, 2017.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from app.services.ml.risk_scoring import RiskIndicator


def additive_shap_for_indicators(
    indicators: List["RiskIndicator"],
    weights: Dict[str, float],
    neutral_baseline: float = 50.0,
    per_feature_baseline: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Calcula atribuições exactas (equivalentes a SHAP LinearExplainer com baseline constante).

    :param neutral_baseline: valor de referência por indicador (ex.: 50 = “risco neutro”).
    :param per_feature_baseline: opcional, sobrepõe o baseline por nome de indicador.
    """
    bmap = per_feature_baseline or {}
    shap_values: Dict[str, float] = {}
    for ind in indicators:
        b = float(bmap.get(ind.name, neutral_baseline))
        w = float(ind.weight)
        v = float(ind.value)
        shap_values[ind.name] = round(w * (v - b), 4)

    base_value = round(
        sum(weights[name] * float(bmap.get(name, neutral_baseline)) for name in weights.keys()),
        4,
    )
    pred_raw = round(sum(ind.value * ind.weight for ind in indicators), 4)
    shap_sum = round(sum(shap_values.values()), 4)

    return {
        "explainer": "exact_additive_shapley",
        "model_family": "weighted_linear_indicators",
        "neutral_baseline": neutral_baseline,
        "base_value": base_value,
        "prediction_raw": pred_raw,
        "shap_values": shap_values,
        "shap_sum": shap_sum,
        "residual_check": round(pred_raw - base_value - shap_sum, 6),
        "documentation": "https://shap.readthedocs.io/en/latest/example_notebooks/api_examples/explainers/Linear.html",
    }
