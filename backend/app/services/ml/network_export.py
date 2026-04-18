"""Serialização do grafo de investigação (GraphML / JSON)."""

from __future__ import annotations

import io
import json
from typing import Literal, Tuple

import networkx as nx
from networkx.readwrite import json_graph

from app.domain.investigation import Investigation
from app.services.ml.network_analysis import NetworkAnalysisEngine


def _xml_safe_attr(value: object) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    return str(value)[:4000]


def export_investigation_graph(
    inv: Investigation,
    fmt: Literal["json", "graphml"],
) -> Tuple[str, str]:
    """
    :returns: (corpo, media_type)
    """
    G = NetworkAnalysisEngine._build_graph(inv)
    if G.number_of_nodes() == 0:
        empty_obj = {
            "directed": False,
            "multigraph": False,
            "graph": {"message": "Sem dados para grafo"},
            "nodes": [],
            "edges": [],
            "meta": {"investigation_id": inv.id},
        }
        empty = json.dumps(empty_obj, ensure_ascii=False)
        return empty, "application/json; charset=utf-8"

    if fmt == "json":
        data = json_graph.node_link_data(G)
        data["meta"] = {
            "investigation_id": inv.id,
            "target_name": inv.target_name,
            "format": "node_link",
        }
        return (
            json.dumps(data, ensure_ascii=False, indent=2),
            "application/json; charset=utf-8",
        )

    H = nx.Graph()
    for n, attrs in G.nodes(data=True):
        clean = {str(k): _xml_safe_attr(v) for k, v in attrs.items()}
        H.add_node(str(n), **clean)
    for u, v, attrs in G.edges(data=True):
        clean_e = {str(k): _xml_safe_attr(v) for k, v in attrs.items()}
        H.add_edge(str(u), str(v), **clean_e)
    buf = io.BytesIO()
    nx.write_graphml(H, buf, encoding="utf-8")
    return buf.getvalue().decode("utf-8"), "application/xml; charset=utf-8"
