"""Ajustes de ambiente para execucao local a partir da raiz do repositorio."""

from __future__ import annotations

import warnings

warnings.filterwarnings(
    "ignore",
    message=r".*logfire-plugin.*",
    category=UserWarning,
    module=r"pydantic\.plugin\._loader",
)
