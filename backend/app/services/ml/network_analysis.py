"""
Análise de rede para investigações (estrutura mínima para API e testes).

Pode ser expandida com NetworkX e consultas reais à base.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NetworkNode:
    id: str
    label: str
    type: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkEdge:
    source: str
    target: str
    type: str
    weight: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NetworkAnalysis:
    num_nodes: int = 0
    num_edges: int = 0
    density: float = 0.0
    central_nodes: List[Tuple[str, float]] = field(default_factory=list)
    communities: List[List[str]] = field(default_factory=list)
    clusters: int = 0
    key_players: List[str] = field(default_factory=list)
    suspicious_patterns: List[str] = field(default_factory=list)
    graph_data: Dict[str, Any] = field(
        default_factory=lambda: {"nodes": [], "edges": []}
    )


class NetworkAnalysisEngine:
    @staticmethod
    async def analyze_network(db: Any, investigation_id: int) -> NetworkAnalysis:
        return NetworkAnalysis()

    @staticmethod
    async def find_shortest_path(
        db: Any,
        investigation_id: int,
        source: str,
        target: str,
    ) -> Optional[List[str]]:
        return None

    @staticmethod
    async def find_all_connections(
        db: Any,
        investigation_id: int,
        entity_id: str,
        max_depth: int = 2,
    ) -> List[Dict[str, Any]]:
        return []
