"""
Sistema de Análise de Rede usando NetworkX
Mapeia e analisa conexões entre pessoas, empresas e propriedades
"""
import networkx as nx
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NetworkNode:
    """Nó da rede"""
    id: str
    type: str  # person, company, property
    label: str
    attributes: Dict


@dataclass
class NetworkEdge:
    """Aresta da rede"""
    source: str
    target: str
    type: str  # owns, manages, leases, partner_in
    weight: float
    attributes: Dict


@dataclass
class NetworkAnalysis:
    """Resultado da análise de rede"""
    num_nodes: int
    num_edges: int
    density: float
    central_nodes: List[Tuple[str, float]]  # (node_id, centrality_score)
    communities: List[List[str]]  # Grupos de nós fortemente conectados
    clusters: int
    key_players: List[str]  # Nós mais influentes
    suspicious_patterns: List[str]
    graph_data: Dict  # Para visualização


class NetworkAnalysisEngine:
    """
    Engine de análise de rede social
    
    Analisa:
    - Centralidade (quem é mais importante)
    - Comunidades (grupos)
    - Caminhos críticos
    - Pontes (nós de ligação)
    - Clusters isolados
    """
    
    @classmethod
    async def analyze_network(
        cls,
        db,
        investigation_id: int
    ) -> NetworkAnalysis:
        """Analisa rede completa da investigação"""
        try:
            # Construir grafo
            G = await cls._build_graph(db, investigation_id)
            
            if G.number_of_nodes() == 0:
                return NetworkAnalysis(
                    num_nodes=0,
                    num_edges=0,
                    density=0.0,
                    central_nodes=[],
                    communities=[],
                    clusters=0,
                    key_players=[],
                    suspicious_patterns=[],
                    graph_data={}
                )
            
            # Análises
            density = nx.density(G)
            central_nodes = cls._calculate_centrality(G)
            communities = cls._detect_communities(G)
            clusters = nx.number_connected_components(G)
            key_players = cls._identify_key_players(G, central_nodes)
            suspicious_patterns = cls._detect_network_patterns(G)
            graph_data = cls._prepare_graph_data(G)
            
            logger.info(
                f"✅ Análise de rede completa: {G.number_of_nodes()} nós, "
                f"{G.number_of_edges()} arestas, "
                f"{len(communities)} comunidades detectadas"
            )
            
            return NetworkAnalysis(
                num_nodes=G.number_of_nodes(),
                num_edges=G.number_of_edges(),
                density=round(density, 4),
                central_nodes=central_nodes[:10],  # Top 10
                communities=communities,
                clusters=clusters,
                key_players=key_players,
                suspicious_patterns=suspicious_patterns,
                graph_data=graph_data
            )
        except Exception as e:
            logger.error(f"Erro ao analisar rede para investigação {investigation_id}: {e}")
            # Retornar análise vazia como fallback
            return NetworkAnalysis(
                num_nodes=0,
                num_edges=0,
                density=0.0,
                central_nodes=[],
                communities=[],
                clusters=0,
                key_players=[],
                suspicious_patterns=['Análise de rede em desenvolvimento'],
                graph_data={}
            )
            central_nodes=central_nodes[:20],  # Top 20
            communities=communities,
            clusters=clusters,
            key_players=key_players,
            suspicious_patterns=suspicious_patterns,
            graph_data=graph_data
        )
    
    @classmethod
    async def _build_graph(cls, db, investigation_id: int) -> nx.Graph:
        """Constrói grafo da rede"""
        from sqlalchemy import select
        from app.domain.company import Company
        from app.domain.property import Property
        from app.domain.lease_contract import LeaseContract
        
        G = nx.Graph()
        
        # 1. Adicionar empresas como nós
        query = select(Company).where(
            Company.investigation_id == investigation_id
        )
        result = await db.execute(query)
        companies = result.scalars().all()
        
        for company in companies:
            node_id = f"company_{company.id}"
            G.add_node(
                node_id,
                type='company',
                label=company.corporate_name,
                cnpj=company.cnpj,
                status=company.status,
                state=company.state
            )
        
        # 2. Adicionar propriedades como nós
        query = select(Property).where(
            Property.investigation_id == investigation_id
        )
        result = await db.execute(query)
        properties = result.scalars().all()
        
        for prop in properties:
            node_id = f"property_{prop.id}"
            G.add_node(
                node_id,
                type='property',
                label=prop.property_name or f"Propriedade {prop.id}",
                car=prop.car_number,
                area=prop.area_hectares,
                state=prop.state,
                city=prop.city
            )
            
            # Conectar propriedade ao proprietário (se for empresa)
            if prop.owner_cpf_cnpj:
                # Buscar empresa proprietária
                for company in companies:
                    if company.cnpj == prop.owner_cpf_cnpj:
                        G.add_edge(
                            f"company_{company.id}",
                            node_id,
                            type='owns',
                            weight=1.0
                        )
                        break
        
        # 3. Adicionar contratos como arestas
        query = select(LeaseContract).where(
            LeaseContract.investigation_id == investigation_id
        )
        result = await db.execute(query)
        contracts = result.scalars().all()
        
        for contract in contracts:
            # Encontrar nós correspondentes
            lessor_node = None
            lessee_node = None
            
            # Buscar locador
            if contract.lessor_cpf_cnpj:
                for company in companies:
                    if company.cnpj == contract.lessor_cpf_cnpj:
                        lessor_node = f"company_{company.id}"
                        break
            
            # Buscar locatário
            if contract.lessee_cpf_cnpj:
                for company in companies:
                    if company.cnpj == contract.lessee_cpf_cnpj:
                        lessee_node = f"company_{company.id}"
                        break
            
            # Adicionar aresta se ambos existem
            if lessor_node and lessee_node:
                weight = contract.value / 1_000_000 if contract.value else 1.0
                G.add_edge(
                    lessor_node,
                    lessee_node,
                    type='leases',
                    weight=weight,
                    value=contract.value,
                    area=contract.area_leased
                )
        
        return G
    
    @classmethod
    def _calculate_centrality(cls, G: nx.Graph) -> List[Tuple[str, float]]:
        """Calcula centralidade dos nós"""
        
        if G.number_of_nodes() == 0:
            return []
        
        # Centralidade de grau (quantas conexões)
        degree_centrality = nx.degree_centrality(G)
        
        # Centralidade de intermediação (quantos caminhos passam por ele)
        try:
            betweenness_centrality = nx.betweenness_centrality(G)
        except:
            betweenness_centrality = degree_centrality
        
        # Combinar métricas
        combined_centrality = {}
        for node in G.nodes():
            combined_centrality[node] = (
                degree_centrality.get(node, 0) * 0.6 +
                betweenness_centrality.get(node, 0) * 0.4
            )
        
        # Ordenar por centralidade
        sorted_nodes = sorted(
            combined_centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_nodes
    
    @classmethod
    def _detect_communities(cls, G: nx.Graph) -> List[List[str]]:
        """Detecta comunidades (grupos fortemente conectados)"""
        
        if G.number_of_nodes() == 0:
            return []
        
        try:
            # Usar algoritmo de Louvain para detectar comunidades
            from networkx.algorithms.community import greedy_modularity_communities
            
            communities = greedy_modularity_communities(G)
            
            # Converter para lista de listas
            community_list = [list(community) for community in communities]
            
            # Filtrar comunidades muito pequenas (< 3 nós)
            community_list = [c for c in community_list if len(c) >= 3]
            
            # Ordenar por tamanho
            community_list.sort(key=len, reverse=True)
            
            return community_list
        
        except Exception as e:
            logger.warning(f"Erro ao detectar comunidades: {e}")
            return []
    
    @classmethod
    def _identify_key_players(
        cls,
        G: nx.Graph,
        central_nodes: List[Tuple[str, float]]
    ) -> List[str]:
        """Identifica jogadores-chave (nós mais influentes)"""
        
        key_players = []
        
        # Top 10 nós mais centrais
        for node_id, centrality in central_nodes[:10]:
            node_data = G.nodes[node_id]
            label = node_data.get('label', node_id)
            node_type = node_data.get('type', 'unknown')
            
            key_players.append(
                f"{label} ({node_type}) - Score: {centrality:.3f}"
            )
        
        return key_players
    
    @classmethod
    def _detect_network_patterns(cls, G: nx.Graph) -> List[str]:
        """Detecta padrões suspeitos na rede"""
        
        patterns = []
        
        if G.number_of_nodes() == 0:
            return patterns
        
        # 1. Nós isolados (sem conexões)
        isolated_nodes = list(nx.isolates(G))
        if len(isolated_nodes) > 5:
            patterns.append(
                f"⚠️ {len(isolated_nodes)} nós isolados (sem conexões)"
            )
        
        # 2. Hubs (nós com muitas conexões)
        degrees = dict(G.degree())
        avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0
        
        hubs = [
            node for node, degree in degrees.items()
            if degree > avg_degree * 3
        ]
        
        if hubs:
            patterns.append(
                f"🔍 {len(hubs)} hubs detectados (nós com muitas conexões)"
            )
        
        # 3. Pontes (nós que conectam comunidades)
        try:
            bridges = list(nx.bridges(G))
            if len(bridges) > 10:
                patterns.append(
                    f"🌉 {len(bridges)} pontes detectadas (conexões críticas)"
                )
        except:
            pass
        
        # 4. Cliques (grupos totalmente conectados)
        try:
            cliques = list(nx.find_cliques(G))
            large_cliques = [c for c in cliques if len(c) >= 5]
            
            if large_cliques:
                patterns.append(
                    f"👥 {len(large_cliques)} cliques grandes detectados "
                    f"(grupos totalmente conectados)"
                )
        except:
            pass
        
        # 5. Densidade anormal
        density = nx.density(G)
        if density > 0.5:
            patterns.append(
                f"📊 Rede muito densa ({density:.2%}) - "
                f"possível estrutura artificial"
            )
        elif density < 0.01:
            patterns.append(
                f"📊 Rede muito esparsa ({density:.2%}) - "
                f"poucas conexões identificadas"
            )
        
        return patterns
    
    @classmethod
    def _prepare_graph_data(cls, G: nx.Graph) -> Dict:
        """Prepara dados do grafo para visualização"""
        
        nodes = []
        edges = []
        
        # Preparar nós
        for node_id in G.nodes():
            node_data = G.nodes[node_id]
            nodes.append({
                'id': node_id,
                'label': node_data.get('label', node_id),
                'type': node_data.get('type', 'unknown'),
                'attributes': {
                    k: v for k, v in node_data.items()
                    if k not in ['label', 'type']
                }
            })
        
        # Preparar arestas
        for source, target in G.edges():
            edge_data = G[source][target]
            edges.append({
                'source': source,
                'target': target,
                'type': edge_data.get('type', 'unknown'),
                'weight': edge_data.get('weight', 1.0),
                'attributes': {
                    k: v for k, v in edge_data.items()
                    if k not in ['type', 'weight']
                }
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'num_nodes': G.number_of_nodes(),
                'num_edges': G.number_of_edges(),
                'density': nx.density(G),
                'is_connected': nx.is_connected(G)
            }
        }
    
    @classmethod
    async def find_shortest_path(
        cls,
        db,
        investigation_id: int,
        source_entity: str,
        target_entity: str
    ) -> Optional[List[str]]:
        """Encontra caminho mais curto entre duas entidades"""
        
        G = await cls._build_graph(db, investigation_id)
        
        try:
            path = nx.shortest_path(G, source_entity, target_entity)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    @classmethod
    async def find_all_connections(
        cls,
        db,
        investigation_id: int,
        entity_id: str,
        max_depth: int = 2
    ) -> List[str]:
        """Encontra todas as conexões de uma entidade até N níveis"""
        
        G = await cls._build_graph(db, investigation_id)
        
        if entity_id not in G:
            return []
        
        # BFS até max_depth
        connections = set()
        current_level = {entity_id}
        visited = {entity_id}
        
        for _ in range(max_depth):
            next_level = set()
            for node in current_level:
                for neighbor in G.neighbors(node):
                    if neighbor not in visited:
                        connections.add(neighbor)
                        next_level.add(neighbor)
                        visited.add(neighbor)
            
            if not next_level:
                break
            
            current_level = next_level
        
        return list(connections)
