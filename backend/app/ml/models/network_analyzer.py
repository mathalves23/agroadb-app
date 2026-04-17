"""
Network Analyzer - Análise de Redes e Relacionamentos

Este módulo utiliza teoria de grafos para analisar relacionamentos entre
pessoas, empresas e propriedades em investigações patrimoniais.

Análises realizadas:
- Mapeamento de redes de relacionamentos
- Identificação de atores centrais (hub nodes)
- Detecção de comunidades/clusters
- Caminhos suspeitos entre entidades
- Grau de conexão entre entidades
- Análise de centralidade
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from sqlalchemy.orm import Session
from collections import defaultdict, deque
import logging
import json

from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company
from app.domain.lease_contract import LeaseContract

logger = logging.getLogger(__name__)


class Node:
    """Representa um nó (pessoa ou empresa) na rede"""
    
    def __init__(
        self,
        node_id: str,
        node_type: str,  # "person", "company", "property"
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.node_id,
            "type": self.node_type,
            "name": self.name,
            "metadata": self.metadata
        }


class Edge:
    """Representa uma conexão entre dois nós"""
    
    def __init__(
        self,
        source: str,
        target: str,
        relationship_type: str,  # "owns", "partner", "leases", "related"
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.source = source
        self.target = target
        self.relationship_type = relationship_type
        self.weight = weight
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.relationship_type,
            "weight": self.weight,
            "metadata": self.metadata
        }


class NetworkGraph:
    """Representa o grafo completo da rede"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
    
    def add_node(self, node: Node):
        """Adiciona um nó ao grafo"""
        self.nodes[node.node_id] = node
    
    def add_edge(self, edge: Edge):
        """Adiciona uma aresta ao grafo"""
        self.edges.append(edge)
        self.adjacency[edge.source].append(edge.target)
        self.adjacency[edge.target].append(edge.source)  # Grafo não-direcionado
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Retorna vizinhos de um nó"""
        return self.adjacency.get(node_id, [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário (formato D3.js compatível)"""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "statistics": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": self._count_node_types(),
                "edge_types": self._count_edge_types()
            }
        }
    
    def _count_node_types(self) -> Dict[str, int]:
        """Conta nós por tipo"""
        counts = defaultdict(int)
        for node in self.nodes.values():
            counts[node.node_type] += 1
        return dict(counts)
    
    def _count_edge_types(self) -> Dict[str, int]:
        """Conta arestas por tipo"""
        counts = defaultdict(int)
        for edge in self.edges:
            counts[edge.relationship_type] += 1
        return dict(counts)


class CentralityMetrics:
    """Métricas de centralidade para um nó"""
    
    def __init__(
        self,
        node_id: str,
        degree_centrality: float,
        betweenness_centrality: float,
        closeness_centrality: float,
        eigenvector_centrality: float
    ):
        self.node_id = node_id
        self.degree_centrality = degree_centrality
        self.betweenness_centrality = betweenness_centrality
        self.closeness_centrality = closeness_centrality
        self.eigenvector_centrality = eigenvector_centrality
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "node_id": self.node_id,
            "degree_centrality": round(self.degree_centrality, 3),
            "betweenness_centrality": round(self.betweenness_centrality, 3),
            "closeness_centrality": round(self.closeness_centrality, 3),
            "eigenvector_centrality": round(self.eigenvector_centrality, 3),
            "average_centrality": round(
                (self.degree_centrality + self.betweenness_centrality + 
                 self.closeness_centrality + self.eigenvector_centrality) / 4,
                3
            )
        }


class Community:
    """Representa uma comunidade (cluster) na rede"""
    
    def __init__(self, community_id: int, members: List[str]):
        self.community_id = community_id
        self.members = members
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.community_id,
            "size": len(self.members),
            "members": self.members
        }


class NetworkAnalysisResult:
    """Resultado completo da análise de rede"""
    
    def __init__(
        self,
        investigation_id: int,
        graph: NetworkGraph,
        central_actors: List[Tuple[str, CentralityMetrics]],
        communities: List[Community],
        suspicious_paths: List[List[str]],
        analyzed_at: datetime
    ):
        self.investigation_id = investigation_id
        self.graph = graph
        self.central_actors = central_actors
        self.communities = communities
        self.suspicious_paths = suspicious_paths
        self.analyzed_at = analyzed_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "investigation_id": self.investigation_id,
            "graph": self.graph.to_dict(),
            "central_actors": [
                {
                    "node_id": node_id,
                    "node_name": self.graph.nodes.get(node_id, Node("", "", "")).name,
                    "metrics": metrics.to_dict()
                }
                for node_id, metrics in self.central_actors
            ],
            "communities": [c.to_dict() for c in self.communities],
            "suspicious_paths": [
                {
                    "path": path,
                    "length": len(path),
                    "nodes": [
                        {
                            "id": node_id,
                            "name": self.graph.nodes.get(node_id, Node("", "", "")).name
                        }
                        for node_id in path
                    ]
                }
                for path in self.suspicious_paths
            ],
            "analyzed_at": self.analyzed_at.isoformat(),
            "summary": {
                "total_nodes": len(self.graph.nodes),
                "total_edges": len(self.graph.edges),
                "total_communities": len(self.communities),
                "total_suspicious_paths": len(self.suspicious_paths),
                "network_density": self._calculate_density(),
                "average_degree": self._calculate_average_degree()
            }
        }
    
    def _calculate_density(self) -> float:
        """Calcula densidade da rede"""
        n = len(self.graph.nodes)
        if n <= 1:
            return 0.0
        max_edges = n * (n - 1) / 2
        return len(self.graph.edges) / max_edges if max_edges > 0 else 0.0
    
    def _calculate_average_degree(self) -> float:
        """Calcula grau médio dos nós"""
        if not self.graph.nodes:
            return 0.0
        total_degree = sum(len(neighbors) for neighbors in self.graph.adjacency.values())
        return total_degree / len(self.graph.nodes)


class NetworkAnalyzer:
    """
    Analisador de Redes e Relacionamentos
    
    Constrói e analisa o grafo de relacionamentos entre:
    - Pessoas (CPFs)
    - Empresas (CNPJs)
    - Propriedades
    
    Realiza:
    - Análise de centralidade (quem são os atores principais)
    - Detecção de comunidades (grupos relacionados)
    - Identificação de caminhos suspeitos
    - Cálculo de métricas de rede
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze(self, investigation_id: int) -> NetworkAnalysisResult:
        """
        Analisa a rede de relacionamentos de uma investigação
        
        Args:
            investigation_id: ID da investigação
            
        Returns:
            NetworkAnalysisResult com grafo e análises
        """
        logger.info(f"Iniciando análise de rede para investigação {investigation_id}")
        
        # Buscar investigação
        investigation = self.db.query(Investigation).filter(
            Investigation.id == investigation_id
        ).first()
        
        if not investigation:
            raise ValueError(f"Investigação {investigation_id} não encontrada")
        
        # 1. Construir grafo
        graph = self._build_graph(investigation)
        
        # 2. Calcular centralidade
        central_actors = self._calculate_centrality(graph)
        
        # 3. Detectar comunidades
        communities = self._detect_communities(graph)
        
        # 4. Encontrar caminhos suspeitos
        suspicious_paths = self._find_suspicious_paths(graph, investigation)
        
        result = NetworkAnalysisResult(
            investigation_id=investigation_id,
            graph=graph,
            central_actors=central_actors,
            communities=communities,
            suspicious_paths=suspicious_paths,
            analyzed_at=datetime.utcnow()
        )
        
        logger.info(
            f"Análise concluída: {len(graph.nodes)} nós, {len(graph.edges)} arestas, "
            f"{len(communities)} comunidades"
        )
        
        return result
    
    def _build_graph(self, investigation: Investigation) -> NetworkGraph:
        """Constrói o grafo de relacionamentos"""
        graph = NetworkGraph()
        
        # Adicionar alvo da investigação
        target_id = None
        if investigation.target_cpf:
            target_id = f"cpf_{investigation.target_cpf}"
            graph.add_node(Node(
                node_id=target_id,
                node_type="person",
                name=investigation.target_name or "Alvo",
                metadata={"is_target": True, "cpf": investigation.target_cpf}
            ))
        elif investigation.target_cnpj:
            target_id = f"cnpj_{investigation.target_cnpj}"
            graph.add_node(Node(
                node_id=target_id,
                node_type="company",
                name=investigation.target_name or "Alvo",
                metadata={"is_target": True, "cnpj": investigation.target_cnpj}
            ))
        
        # Adicionar propriedades
        for prop in (investigation.properties or []):
            prop_id = f"prop_{prop.id}"
            graph.add_node(Node(
                node_id=prop_id,
                node_type="property",
                name=prop.name or prop.address or "Propriedade",
                metadata={
                    "address": prop.address,
                    "area": prop.additional_data.get("area_hectares") if prop.additional_data else None
                }
            ))
            
            # Conectar propriedade ao alvo
            if target_id:
                graph.add_edge(Edge(
                    source=target_id,
                    target=prop_id,
                    relationship_type="owns",
                    weight=1.0
                ))
            
            # Adicionar proprietários das propriedades
            if prop.additional_data:
                owner_cpf = prop.additional_data.get("owner_cpf")
                owner_cnpj = prop.additional_data.get("owner_cnpj")
                owner_name = prop.additional_data.get("owner_name", "Proprietário")
                
                if owner_cpf:
                    owner_id = f"cpf_{owner_cpf}"
                    if owner_id not in graph.nodes:
                        graph.add_node(Node(
                            node_id=owner_id,
                            node_type="person",
                            name=owner_name,
                            metadata={"cpf": owner_cpf}
                        ))
                    graph.add_edge(Edge(
                        source=owner_id,
                        target=prop_id,
                        relationship_type="owns",
                        weight=1.0
                    ))
                
                if owner_cnpj:
                    owner_id = f"cnpj_{owner_cnpj}"
                    if owner_id not in graph.nodes:
                        graph.add_node(Node(
                            node_id=owner_id,
                            node_type="company",
                            name=owner_name,
                            metadata={"cnpj": owner_cnpj}
                        ))
                    graph.add_edge(Edge(
                        source=owner_id,
                        target=prop_id,
                        relationship_type="owns",
                        weight=1.0
                    ))
        
        # Adicionar empresas e sócios
        for company in (investigation.companies or []):
            company_id = f"cnpj_{company.cnpj}"
            if company_id not in graph.nodes:
                graph.add_node(Node(
                    node_id=company_id,
                    node_type="company",
                    name=company.name,
                    metadata={
                        "cnpj": company.cnpj,
                        "status": company.additional_data.get("status") if company.additional_data else None
                    }
                ))
            
            # Conectar empresa ao alvo (se for o caso)
            if target_id and target_id != company_id:
                graph.add_edge(Edge(
                    source=target_id,
                    target=company_id,
                    relationship_type="related",
                    weight=0.8
                ))
            
            # Adicionar sócios
            if company.additional_data:
                partners = company.additional_data.get("partners", [])
                for partner in partners:
                    partner_cpf = partner.get("cpf")
                    partner_cnpj = partner.get("cnpj")
                    partner_name = partner.get("name", "Sócio")
                    partner_share = float(partner.get("share", 0))
                    
                    if partner_cpf:
                        partner_id = f"cpf_{partner_cpf}"
                        if partner_id not in graph.nodes:
                            graph.add_node(Node(
                                node_id=partner_id,
                                node_type="person",
                                name=partner_name,
                                metadata={"cpf": partner_cpf}
                            ))
                        graph.add_edge(Edge(
                            source=partner_id,
                            target=company_id,
                            relationship_type="partner",
                            weight=partner_share / 100 if partner_share > 0 else 0.5,
                            metadata={"share_percentage": partner_share}
                        ))
                    
                    elif partner_cnpj:
                        partner_id = f"cnpj_{partner_cnpj}"
                        if partner_id not in graph.nodes:
                            graph.add_node(Node(
                                node_id=partner_id,
                                node_type="company",
                                name=partner_name,
                                metadata={"cnpj": partner_cnpj}
                            ))
                        graph.add_edge(Edge(
                            source=partner_id,
                            target=company_id,
                            relationship_type="partner",
                            weight=partner_share / 100 if partner_share > 0 else 0.5,
                            metadata={"share_percentage": partner_share}
                        ))
        
        # Adicionar arrendamentos
        for lease in (investigation.lease_contracts or []):
            lessor_name = lease.lessor_name
            lessee_name = lease.lessee_name
            
            if lessor_name and lessee_name:
                # Criar IDs genéricos (idealmente buscaríamos CPF/CNPJ)
                lessor_id = f"entity_{lessor_name.replace(' ', '_')}"
                lessee_id = f"entity_{lessee_name.replace(' ', '_')}"
                
                # Adicionar nós se não existirem
                if lessor_id not in graph.nodes:
                    graph.add_node(Node(
                        node_id=lessor_id,
                        node_type="person",
                        name=lessor_name,
                        metadata={}
                    ))
                
                if lessee_id not in graph.nodes:
                    graph.add_node(Node(
                        node_id=lessee_id,
                        node_type="person",
                        name=lessee_name,
                        metadata={}
                    ))
                
                # Adicionar aresta de arrendamento
                graph.add_edge(Edge(
                    source=lessor_id,
                    target=lessee_id,
                    relationship_type="leases",
                    weight=0.6,
                    metadata={
                        "monthly_value": lease.monthly_value,
                        "start_date": lease.start_date.isoformat() if lease.start_date else None,
                        "end_date": lease.end_date.isoformat() if lease.end_date else None
                    }
                ))
        
        return graph
    
    def _calculate_centrality(
        self,
        graph: NetworkGraph
    ) -> List[Tuple[str, CentralityMetrics]]:
        """
        Calcula métricas de centralidade para todos os nós
        
        Identifica os atores mais importantes da rede
        """
        centrality_list = []
        
        for node_id in graph.nodes.keys():
            # 1. Degree Centrality (número de conexões)
            degree = len(graph.get_neighbors(node_id))
            max_degree = len(graph.nodes) - 1
            degree_centrality = degree / max_degree if max_degree > 0 else 0.0
            
            # 2. Betweenness Centrality (quantos caminhos passam por este nó)
            betweenness = self._calculate_betweenness(graph, node_id)
            
            # 3. Closeness Centrality (quão próximo está dos outros nós)
            closeness = self._calculate_closeness(graph, node_id)
            
            # 4. Eigenvector Centrality (conexões com nós importantes)
            eigenvector = self._calculate_eigenvector(graph, node_id)
            
            metrics = CentralityMetrics(
                node_id=node_id,
                degree_centrality=degree_centrality,
                betweenness_centrality=betweenness,
                closeness_centrality=closeness,
                eigenvector_centrality=eigenvector
            )
            
            centrality_list.append((node_id, metrics))
        
        # Ordenar por centralidade média (top 10)
        centrality_list.sort(
            key=lambda x: (
                x[1].degree_centrality + x[1].betweenness_centrality +
                x[1].closeness_centrality + x[1].eigenvector_centrality
            ) / 4,
            reverse=True
        )
        
        return centrality_list[:10]
    
    def _calculate_betweenness(self, graph: NetworkGraph, node_id: str) -> float:
        """Calcula betweenness centrality (simplificado)"""
        # Versão simplificada: conta quantos pares de nós têm caminho passando por este nó
        paths_through = 0
        total_paths = 0
        
        all_nodes = list(graph.nodes.keys())
        for i, source in enumerate(all_nodes):
            if source == node_id:
                continue
            for target in all_nodes[i+1:]:
                if target == node_id:
                    continue
                
                # BFS para encontrar caminho mais curto
                path = self._bfs_shortest_path(graph, source, target)
                if path:
                    total_paths += 1
                    if node_id in path[1:-1]:  # Nó está no meio do caminho
                        paths_through += 1
        
        return paths_through / total_paths if total_paths > 0 else 0.0
    
    def _calculate_closeness(self, graph: NetworkGraph, node_id: str) -> float:
        """Calcula closeness centrality"""
        # Soma das distâncias mínimas para todos os outros nós
        distances = []
        
        for target_id in graph.nodes.keys():
            if target_id == node_id:
                continue
            
            distance = self._bfs_distance(graph, node_id, target_id)
            if distance > 0:
                distances.append(distance)
        
        if not distances:
            return 0.0
        
        avg_distance = sum(distances) / len(distances)
        return 1.0 / avg_distance if avg_distance > 0 else 0.0
    
    def _calculate_eigenvector(self, graph: NetworkGraph, node_id: str) -> float:
        """Calcula eigenvector centrality (simplificado)"""
        # Versão simplificada: média das centralidades dos vizinhos
        neighbors = graph.get_neighbors(node_id)
        if not neighbors:
            return 0.0
        
        # Usar degree centrality dos vizinhos como proxy
        neighbor_centralities = []
        max_degree = len(graph.nodes) - 1
        
        for neighbor_id in neighbors:
            neighbor_degree = len(graph.get_neighbors(neighbor_id))
            neighbor_centralities.append(neighbor_degree / max_degree if max_degree > 0 else 0.0)
        
        return sum(neighbor_centralities) / len(neighbor_centralities)
    
    def _bfs_shortest_path(
        self,
        graph: NetworkGraph,
        source: str,
        target: str
    ) -> Optional[List[str]]:
        """BFS para encontrar caminho mais curto"""
        if source == target:
            return [source]
        
        visited = {source}
        queue = deque([(source, [source])])
        
        while queue:
            node, path = queue.popleft()
            
            for neighbor in graph.get_neighbors(node):
                if neighbor == target:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def _bfs_distance(self, graph: NetworkGraph, source: str, target: str) -> int:
        """BFS para calcular distância"""
        path = self._bfs_shortest_path(graph, source, target)
        return len(path) - 1 if path else -1
    
    def _detect_communities(self, graph: NetworkGraph) -> List[Community]:
        """
        Detecta comunidades (clusters) na rede usando algoritmo de Louvain simplificado
        """
        # Versão simplificada: usar componentes conectados
        visited = set()
        communities = []
        community_id = 0
        
        for node_id in graph.nodes.keys():
            if node_id not in visited:
                # BFS para encontrar componente conectado
                component = self._bfs_component(graph, node_id, visited)
                if len(component) >= 2:  # Pelo menos 2 nós
                    communities.append(Community(
                        community_id=community_id,
                        members=component
                    ))
                    community_id += 1
        
        # Ordenar por tamanho
        communities.sort(key=lambda c: len(c.members), reverse=True)
        
        return communities
    
    def _bfs_component(
        self,
        graph: NetworkGraph,
        start_node: str,
        visited: Set[str]
    ) -> List[str]:
        """BFS para encontrar componente conectado"""
        component = []
        queue = deque([start_node])
        visited.add(start_node)
        
        while queue:
            node = queue.popleft()
            component.append(node)
            
            for neighbor in graph.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return component
    
    def _find_suspicious_paths(
        self,
        graph: NetworkGraph,
        investigation: Investigation
    ) -> List[List[str]]:
        """
        Encontra caminhos suspeitos na rede
        
        Suspeitos:
        - Caminhos muito longos entre entidades relacionadas
        - Caminhos envolvendo empresas offshore
        - Caminhos circulares (A -> B -> C -> A)
        """
        suspicious_paths = []
        
        # 1. Encontrar caminhos longos (> 4 nós)
        target_id = None
        if investigation.target_cpf:
            target_id = f"cpf_{investigation.target_cpf}"
        elif investigation.target_cnpj:
            target_id = f"cnpj_{investigation.target_cnpj}"
        
        if target_id and target_id in graph.nodes:
            for node_id in graph.nodes.keys():
                if node_id == target_id:
                    continue
                
                path = self._bfs_shortest_path(graph, target_id, node_id)
                if path and len(path) > 4:
                    suspicious_paths.append(path)
        
        # 2. Encontrar ciclos (A -> B -> ... -> A)
        cycles = self._find_cycles(graph)
        suspicious_paths.extend(cycles)
        
        # Limitar a 10 caminhos mais suspeitos
        return suspicious_paths[:10]
    
    def _find_cycles(self, graph: NetworkGraph) -> List[List[str]]:
        """Encontra ciclos no grafo"""
        cycles = []
        visited = set()
        
        def dfs_cycle(node: str, path: List[str], parent: Optional[str] = None):
            """DFS para encontrar ciclos"""
            visited.add(node)
            path.append(node)
            
            for neighbor in graph.get_neighbors(node):
                if neighbor == parent:
                    continue
                
                if neighbor in path:
                    # Ciclo encontrado
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if len(cycle) >= 3 and len(cycle) <= 6:  # Ciclos de 3 a 6 nós
                        cycles.append(cycle)
                elif neighbor not in visited:
                    dfs_cycle(neighbor, path.copy(), node)
        
        for start_node in graph.nodes.keys():
            if start_node not in visited:
                dfs_cycle(start_node, [])
        
        # Remover duplicatas
        unique_cycles = []
        seen_cycles = set()
        
        for cycle in cycles:
            # Normalizar ciclo (começar do menor ID)
            normalized = tuple(sorted(cycle))
            if normalized not in seen_cycles:
                seen_cycles.add(normalized)
                unique_cycles.append(cycle)
        
        return unique_cycles[:5]  # Top 5 ciclos
