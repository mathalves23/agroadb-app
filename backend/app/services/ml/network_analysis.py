"""
Análise de rede para investigações (NetworkX + dados reais da base).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.investigation import InvestigationRepository


def _clean_doc(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r"\D", "", s)


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
        default_factory=lambda: {"nodes": [], "links": []}
    )


class NetworkAnalysisEngine:
    @staticmethod
    async def analyze_network(db: AsyncSession, investigation_id: int) -> NetworkAnalysis:
        repo = InvestigationRepository(db)
        inv = await repo.get_with_relations(investigation_id)
        if not inv:
            return NetworkAnalysis(
                suspicious_patterns=["Investigação não encontrada"],
            )

        G = nx.Graph()
        root = f"inv:{inv.id}"
        G.add_node(
            root,
            label=inv.target_name[:80],
            node_type="investigation",
        )

        for p in inv.properties or []:
            nid = f"prop:{p.id}"
            lbl = (p.property_name or p.car_number or p.matricula or f"Imóvel {p.id}")[:80]
            G.add_node(
                nid,
                label=lbl,
                node_type="property",
                state=p.state or "",
            )
            G.add_edge(root, nid, relation="possui_imovel")
            owner = _clean_doc(p.owner_cpf_cnpj)
            if owner and len(owner) in (11, 14):
                oid = f"doc:{owner}"
                if not G.has_node(oid):
                    G.add_node(oid, label=f"Titular {owner}", node_type="document")
                G.add_edge(nid, oid, relation="titularidade")

        for c in inv.companies or []:
            cid = f"comp:{c.id}"
            lbl = (c.corporate_name or c.trade_name or c.cnpj)[:80]
            G.add_node(cid, label=lbl, node_type="company", cnpj=_clean_doc(c.cnpj))
            G.add_edge(root, cid, relation="empresa_relacionada")
            doc = _clean_doc(c.cnpj)
            if doc:
                oid = f"doc:{doc}"
                if not G.has_node(oid):
                    G.add_node(oid, label=f"CNPJ {doc}", node_type="document")
                G.add_edge(cid, oid, relation="identificacao")

        # ligações fracas: mesmo titular entre imóveis
        doc_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "document"]
        for d1 in doc_nodes:
            neigh = list(G.neighbors(d1))
            props = [n for n in neigh if n.startswith("prop:")]
            if len(props) >= 2:
                for i in range(len(props)):
                    for j in range(i + 1, len(props)):
                        if not G.has_edge(props[i], props[j]):
                            G.add_edge(props[i], props[j], relation="mesmo_titular", weight=0.5)

        if G.number_of_nodes() == 0:
            return NetworkAnalysis(suspicious_patterns=["Sem dados para grafo"])

        density = float(nx.density(G)) if G.number_of_nodes() > 1 else 0.0
        cent = nx.degree_centrality(G)
        central_nodes = sorted(cent.items(), key=lambda x: -x[1])[:8]
        key_players = [n for n, _ in central_nodes if not str(n).startswith("inv:")][:6]

        communities: List[List[str]] = []
        try:
            if G.number_of_nodes() > 2:
                comms = greedy_modularity_communities(G)
                communities = [sorted(list(c)) for c in comms if len(c) > 1][:6]
        except Exception:
            communities = []

        suspicious: List[str] = []
        if density > 0.55 and G.number_of_nodes() > 5:
            suspicious.append("Rede muito densa: revisar duplicidades ou vínculos espúrios")
        if len([n for n in G.nodes if str(n).startswith("doc:")]) > 8:
            suspicious.append("Muitos documentos distintos ligados à mesma investigação")

        nodes_out = []
        for n, data in G.nodes(data=True):
            nodes_out.append(
                {
                    "id": n,
                    "name": data.get("label", n),
                    "val": 1 + int(20 * cent.get(n, 0)),
                    "type": data.get("node_type", "unknown"),
                }
            )
        links_out = []
        for u, v, ed in G.edges(data=True):
            links_out.append(
                {
                    "source": u,
                    "target": v,
                    "name": ed.get("relation", "ligacao"),
                }
            )

        return NetworkAnalysis(
            num_nodes=G.number_of_nodes(),
            num_edges=G.number_of_edges(),
            density=density,
            central_nodes=central_nodes,
            communities=communities,
            clusters=len(communities),
            key_players=key_players,
            suspicious_patterns=suspicious,
            graph_data={"nodes": nodes_out, "links": links_out},
        )

    @staticmethod
    async def find_shortest_path(
        db: AsyncSession,
        investigation_id: int,
        source: str,
        target: str,
    ) -> Optional[List[str]]:
        analysis = await NetworkAnalysisEngine.analyze_network(db, investigation_id)
        links = analysis.graph_data.get("links", [])
        nodes = {n["id"] for n in analysis.graph_data.get("nodes", [])}
        if source not in nodes or target not in nodes:
            return None
        G = nx.Graph()
        for n in analysis.graph_data.get("nodes", []):
            G.add_node(n["id"])
        for e in links:
            G.add_edge(e["source"], e["target"])
        try:
            return nx.shortest_path(G, source, target)
        except Exception:
            return None

    @staticmethod
    async def find_all_connections(
        db: AsyncSession,
        investigation_id: int,
        entity_id: str,
        max_depth: int = 2,
    ) -> List[Dict[str, Any]]:
        analysis = await NetworkAnalysisEngine.analyze_network(db, investigation_id)
        G = nx.Graph()
        for n in analysis.graph_data.get("nodes", []):
            G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
        for e in analysis.graph_data.get("links", []):
            G.add_edge(e["source"], e["target"])
        if entity_id not in G:
            return []
        lengths = nx.single_source_shortest_path_length(G, entity_id, cutoff=max_depth)
        out: List[Dict[str, Any]] = []
        for nid, dist in sorted(lengths.items(), key=lambda x: x[1]):
            if nid == entity_id:
                continue
            out.append({"id": nid, "depth": dist, "label": G.nodes[nid].get("name", nid)})
        return out[:50]
