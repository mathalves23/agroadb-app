"""
Endpoints de Machine Learning e IA
Score de risco, detecção de padrões, análise de rede
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from pydantic import BaseModel

from app.api.v1.deps import get_current_user, get_db
from app.domain.user import User
from app.services.ml.risk_scoring import RiskScoringEngine
from app.services.ml.pattern_detection import PatternDetectionEngine
from app.services.ml.network_analysis import NetworkAnalysisEngine

router = APIRouter()


# ==================== SCHEMAS ====================

class RiskScoreResponse(BaseModel):
    total_score: float
    risk_level: str
    confidence: float
    indicators: list
    patterns_detected: list
    recommendations: list


class PatternDetectionResponse(BaseModel):
    patterns: list
    total_patterns: int
    critical_patterns: int


class NetworkAnalysisResponse(BaseModel):
    num_nodes: int
    num_edges: int
    density: float
    central_nodes: list
    communities: list
    clusters: int
    key_players: list
    suspicious_patterns: list


# ==================== RISK SCORING ====================

@router.get("/investigations/{investigation_id}/risk-score")
async def calculate_risk_score(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Calcula score de risco para uma investigação
    
    **Features:**
    - Score de 0-100
    - 7 indicadores de risco
    - Padrões detectados
    - Recomendações automáticas
    - Nível de confiança
    
    **Níveis de risco:**
    - very_low: 0-20
    - low: 20-40
    - medium: 40-60
    - high: 60-80
    - critical: 80-100
    """
    try:
        # Verificar permissão (simplificado)
        # Em produção, usar collaboration_service
        
        # Calcular score
        risk_score = await RiskScoringEngine.calculate_risk_score(
            db,
            investigation_id
        )
        
        return {
            "total_score": risk_score.total_score,
            "risk_level": risk_score.risk_level,
            "confidence": risk_score.confidence,
            "indicators": [
                {
                    "name": ind.name,
                    "value": ind.value,
                    "weight": ind.weight,
                    "description": ind.description,
                    "severity": ind.severity
                }
                for ind in risk_score.indicators
            ],
            "patterns_detected": risk_score.patterns_detected,
            "recommendations": risk_score.recommendations,
            "timestamp": risk_score.timestamp.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular score de risco: {str(e)}"
        )


# ==================== PATTERN DETECTION ====================

@router.get("/investigations/{investigation_id}/patterns")
async def detect_patterns(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Detecta padrões suspeitos na investigação
    
    **Padrões detectados:**
    - Laranjas (empresas de fachada)
    - Rede suspeita de empresas
    - Transações circulares
    - Concentração anormal de ativos
    - Anomalias temporais
    """
    try:
        patterns = await PatternDetectionEngine.detect_patterns(
            db,
            investigation_id
        )
        
        critical_patterns = [
            p for p in patterns
            if p.severity in ['critical', 'high']
        ]
        
        return {
            "patterns": [
                {
                    "type": p.type,
                    "confidence": p.confidence,
                    "description": p.description,
                    "severity": p.severity,
                    "entities": p.entities,
                    "evidence": p.evidence
                }
                for p in patterns
            ],
            "total_patterns": len(patterns),
            "critical_patterns": len(critical_patterns)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao detectar padrões: {str(e)}"
        )


# ==================== NETWORK ANALYSIS ====================

@router.get("/investigations/{investigation_id}/network")
async def analyze_network(
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Analisa rede de conexões da investigação
    
    **Análises:**
    - Centralidade de nós
    - Comunidades (grupos)
    - Clusters isolados
    - Jogadores-chave
    - Padrões de rede suspeitos
    
    **Retorna:**
    - Dados do grafo para visualização
    - Métricas de rede
    - Análise de centralidade
    """
    try:
        analysis = await NetworkAnalysisEngine.analyze_network(
            db,
            investigation_id
        )
        
        return {
            "num_nodes": analysis.num_nodes,
            "num_edges": analysis.num_edges,
            "density": analysis.density,
            "central_nodes": [
                {"node_id": node, "centrality": cent}
                for node, cent in analysis.central_nodes
            ],
            "communities": [
                {"size": len(comm), "nodes": comm}
                for comm in analysis.communities
            ],
            "clusters": analysis.clusters,
            "key_players": analysis.key_players,
            "suspicious_patterns": analysis.suspicious_patterns,
            "graph_data": analysis.graph_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise de rede: {str(e)}"
        )


@router.get("/investigations/{investigation_id}/network/shortest-path")
async def find_shortest_path(
    investigation_id: int,
    source: str,
    target: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Encontra caminho mais curto entre duas entidades"""
    
    try:
        path = await NetworkAnalysisEngine.find_shortest_path(
            db,
            investigation_id,
            source,
            target
        )
        
        if path:
            return {
                "found": True,
                "path": path,
                "length": len(path) - 1
            }
        else:
            return {
                "found": False,
                "message": "Nenhum caminho encontrado entre as entidades"
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar caminho: {str(e)}"
        )


@router.get("/investigations/{investigation_id}/network/connections")
async def find_connections(
    investigation_id: int,
    entity_id: str,
    max_depth: int = 2,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Encontra todas as conexões de uma entidade até N níveis"""
    
    try:
        connections = await NetworkAnalysisEngine.find_all_connections(
            db,
            investigation_id,
            entity_id,
            max_depth
        )
        
        return {
            "entity_id": entity_id,
            "max_depth": max_depth,
            "connections": connections,
            "total_connections": len(connections)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar conexões: {str(e)}"
        )


# ==================== COMPREHENSIVE ANALYSIS ====================

@router.get("/investigations/{investigation_id}/comprehensive-analysis")
async def comprehensive_analysis(
    investigation_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Análise abrangente completa
    
    Executa em paralelo:
    - Score de risco
    - Detecção de padrões
    - Análise de rede
    
    **Tempo estimado:** 5-15 segundos
    """
    try:
        import asyncio
        
        # Executar análises em paralelo
        risk_task = RiskScoringEngine.calculate_risk_score(db, investigation_id)
        pattern_task = PatternDetectionEngine.detect_patterns(db, investigation_id)
        network_task = NetworkAnalysisEngine.analyze_network(db, investigation_id)
        
        risk_score, patterns, network = await asyncio.gather(
            risk_task,
            pattern_task,
            network_task
        )
        
        # Consolidar resultados
        critical_patterns = [
            p for p in patterns
            if p.severity in ['critical', 'high']
        ]
        
        return {
            "investigation_id": investigation_id,
            "risk": {
                "score": risk_score.total_score,
                "level": risk_score.risk_level,
                "confidence": risk_score.confidence,
                "recommendations": risk_score.recommendations
            },
            "patterns": {
                "total": len(patterns),
                "critical": len(critical_patterns),
                "types": list(set(p.type for p in patterns))
            },
            "network": {
                "nodes": network.num_nodes,
                "edges": network.num_edges,
                "density": network.density,
                "clusters": network.clusters,
                "key_players_count": len(network.key_players)
            },
            "overall_assessment": cls._generate_overall_assessment(
                risk_score,
                patterns,
                network
            )
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise abrangente: {str(e)}"
        )


def _generate_overall_assessment(risk_score, patterns, network) -> dict:
    """Gera avaliação geral consolidada"""
    
    # Contagem de alertas críticos
    critical_alerts = 0
    
    if risk_score.risk_level in ['critical', 'high']:
        critical_alerts += 1
    
    critical_patterns = [
        p for p in patterns
        if p.severity in ['critical', 'high']
    ]
    critical_alerts += len(critical_patterns)
    
    # Avaliação final
    if critical_alerts >= 5:
        assessment = "CRÍTICO"
        color = "red"
    elif critical_alerts >= 3:
        assessment = "ALTO RISCO"
        color = "orange"
    elif critical_alerts >= 1:
        assessment = "MÉDIO RISCO"
        color = "yellow"
    else:
        assessment = "BAIXO RISCO"
        color = "green"
    
    return {
        "assessment": assessment,
        "color": color,
        "critical_alerts": critical_alerts,
        "requires_manual_review": critical_alerts >= 3
    }
