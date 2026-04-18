# Machine Learning — serviços

## Estrutura

```
backend/app/services/ml/
├── risk_scoring.py       # Score de risco (0–100)
├── pattern_detection.py  # Padrões suspeitos
├── network_analysis.py   # Análise de rede (NetworkX)
├── risk_calibration.py   # Calibração opcional (JSON)
└── data/default_risk_calibration.json
```

## Calibração

- Variável `RISK_CALIBRATION_PATH` aponta para JSON produzido offline (base legal e anonimização).
- Treino de calibração: `python scripts/train_risk_calibration.py` (executar a partir de `backend/` com o mesmo ambiente que o resto do projecto).

## Documentação alargada

- Guia de ML e indicadores: [`docs/dev/07-machine-learning.md`](../../../../docs/dev/07-machine-learning.md).
- ADR de calibração linear: [`docs/adr/0002-ml-risk-linear-indicators-calibration.md`](../../../../docs/adr/0002-ml-risk-linear-indicators-calibration.md).
