# ADR-0002: Score de risco como modelo linear de indicadores + calibração opcional

## Estado

Aceite

## Contexto

É necessário um score interpretável (0–100) para investigações patrimoniais, alimentado por dados reais na base (propriedades, contratos, processos, empresas), com possibilidade de **alinhar probabilidades** a conjuntos de referência onde exista base legal, e de **explicar** contribuições por indicador.

## Decisão

1. Manter o motor principal como **soma ponderada** `sum_i w_i * v_i` com `v_i` normalizados em escala 0–100 (`RiskScoringEngine`).
2. Aplicar **calibração pós-processo** opcional via ficheiro JSON (`RISK_CALIBRATION_PATH`): identidade (omissão), `piecewise_linear` ou `scale`, implementado em `app/services/ml/risk_calibration.py`.
3. Expor **atribuições aditivas equivalentes a SHAP** para o modelo linear com baseline neutra configurável (`RISK_SHAP_NEUTRAL_BASELINE`), em `app/services/ml/risk_shap.py`, sem dependência obrigatória da biblioteca `shap`.

## Consequências

- **Positivo:** transparência, auditoria, API estável; calibração pode ser treinada offline (`scripts/train_risk_calibration.py`).
- **Negativo:** calibração não substitui validação jurídica nem rótulos de fraude; rótulos reais exigem compliance explícito.
