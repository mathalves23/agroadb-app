"""
Calibração pós-processo do score de risco (dados reais onde legal).

Suporta ficheiro JSON externo (RISK_CALIBRATION_PATH) ou identidade por omissão.
"""
from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

_DEFAULT_REL = Path(__file__).resolve().parent / "data" / "default_risk_calibration.json"


def _clip_100(x: float) -> float:
    return max(0.0, min(100.0, float(x)))


def _piecewise_y(xs: List[float], ys: List[float], x: float) -> float:
    if not xs or len(xs) != len(ys):
        return x
    pairs = sorted(zip(xs, ys), key=lambda t: t[0])
    if x <= pairs[0][0]:
        return pairs[0][1]
    if x >= pairs[-1][0]:
        return pairs[-1][1]
    for i in range(len(pairs) - 1):
        x0, y0 = pairs[i]
        x1, y1 = pairs[i + 1]
        if x0 <= x <= x1 and x1 != x0:
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return x


@lru_cache(maxsize=4)
def _load_calibration_json(path: str) -> Dict[str, Any]:
    p = Path(path).expanduser()
    if not p.is_file():
        logger.warning("Calibração: ficheiro inexistente %s — a usar identidade", path)
        return {"enabled": False, "method": "identity"}
    try:
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Calibração: erro ao ler %s: %s — identidade", path, exc)
        return {"enabled": False, "method": "identity"}


def load_calibration_config(explicit_path: str | None) -> Dict[str, Any]:
    path = (explicit_path or "").strip()
    if path:
        return _load_calibration_json(os.path.abspath(path))
    if _DEFAULT_REL.is_file():
        return _load_calibration_json(str(_DEFAULT_REL))
    return {"enabled": False, "method": "identity"}


def apply_risk_calibration(raw_score: float, cfg: Dict[str, Any] | None = None) -> Tuple[float, Dict[str, Any]]:
    """
    Aplica transformação monótona ao score bruto [0,100].

    Métodos:
    - identity: sem alteração
    - piecewise_linear: lista ``points`` [[x0,y0],...] interpolação linear
    - scale: ``from_min``, ``from_max``, ``to_min``, ``to_max`` linear + clip
    """
    raw = _clip_100(raw_score)
    if cfg is None:
        cfg = load_calibration_config("")

    meta: Dict[str, Any] = {
        "calibration_enabled": bool(cfg.get("enabled")),
        "method": cfg.get("method", "identity"),
        "trained_on": cfg.get("trained_on"),
        "legal_basis": cfg.get("legal_basis"),
    }

    if not cfg.get("enabled"):
        meta["output"] = "raw_score_unchanged"
        return raw, meta

    method = (cfg.get("method") or "identity").lower()

    if method == "piecewise_linear":
        pts = cfg.get("points") or []
        if not pts:
            meta["error"] = "missing_points"
            return raw, meta
        xs = [float(p[0]) for p in pts]
        ys = [float(p[1]) for p in pts]
        out = _clip_100(_piecewise_y(xs, ys, raw))
        meta["output"] = "piecewise_linear"
        return out, meta

    if method == "scale":
        fm = float(cfg.get("from_min", 0))
        fa = float(cfg.get("from_max", 100))
        tm = float(cfg.get("to_min", 0))
        ta = float(cfg.get("to_max", 100))
        if fa == fm:
            return raw, {**meta, "error": "degenerate_from_range"}
        t = (raw - fm) / (fa - fm)
        out = _clip_100(tm + t * (ta - tm))
        meta["output"] = "linear_scale"
        return out, meta

    meta["output"] = "identity_fallback"
    return raw, meta
