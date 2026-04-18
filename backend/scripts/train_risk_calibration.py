#!/usr/bin/env python3
"""
Treina calibração isotónica ou linear do score de risco a partir de um CSV.

**Requisitos legais:** só use etiquetas (scores alvo) obtidas com base legal
(LGPD, contrato, dados públicos agregados anonimizados, etc.). Não inclua dados
identificáveis sem consentimento.

CSV esperado (exemplo):
    raw_score,target_risk_0_100
    12.5,10
    45.0,38
    ...

Saída: JSON compatível com ``app.services/ml/risk_calibration.py`` (method=piecewise_linear).

Uso:
    python scripts/train_risk_calibration.py --csv dados.csv --out calibracao.json
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from sklearn.isotonic import IsotonicRegression


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--points", type=int, default=12, help="Número de pontos na curva exportada")
    args = p.parse_args()

    xs: list[float] = []
    ys: list[float] = []
    with args.csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            xs.append(float(row["raw_score"]))
            ys.append(float(row["target_risk_0_100"]))

    X = np.array(xs, dtype=float).reshape(-1, 1)
    y = np.array(ys, dtype=float)
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(X.ravel(), y)

    grid = np.linspace(0, 100, args.points)
    mapped = iso.predict(grid)
    points = [[float(a), float(b)] for a, b in zip(grid, mapped)]

    cfg = {
        "enabled": True,
        "method": "piecewise_linear",
        "trained_on": str(args.csv.resolve()),
        "legal_basis": "Definir aqui a base legal do conjunto de treino (editar JSON).",
        "points": points,
    }
    args.out.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(f"Escrito {args.out} com {len(points)} pontos.")


if __name__ == "__main__":
    main()
