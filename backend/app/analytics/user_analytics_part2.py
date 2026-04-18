"""
User Analytics - Parte 2
Heatmaps, Session Recordings e NPS

Continuação do módulo de analytics de usuário.
"""

import random
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.analytics.user_analytics import (
    HeatmapData,
    HeatmapPoint,
    NPSAnalysis,
    NPSResponse,
    SessionEvent,
    SessionRecording,
)
from app.domain.user import User

# ============================================================================
# 3. HEATMAP ANALYTICS
# ============================================================================


class HeatmapAnalytics:
    """
    Análise de Heatmaps de Navegação

    Mapas de calor mostrando onde usuários clicam, scrollam e interagem.
    Identifica zonas quentes e frias para otimização de UX.
    """

    def __init__(self, db: Session):
        self.db = db

        # Páginas rastreadas
        self.TRACKED_PAGES = [
            "/dashboard",
            "/investigations",
            "/investigations/new",
            "/investigations/:id",
            "/reports",
            "/analytics",
            "/settings",
        ]

    def generate_heatmap(
        self,
        page: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: str = "click",  # "click", "scroll", "hover"
    ) -> HeatmapData:
        """
        Gera heatmap para uma página

        Args:
            page: URL da página
            start_date: Data inicial
            end_date: Data final
            event_type: Tipo de evento (click, scroll, hover)

        Returns:
            Dados do heatmap
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()

        # Em produção, viria de tracking de eventos (Hotjar, FullStory, etc)
        # Aqui simulamos dados realistas

        points = self._generate_heatmap_points(page, event_type)

        total_clicks = len(points)
        unique_users = len(set(random.randint(1, 100) for _ in range(total_clicks // 3)))

        # Identificar zonas quentes (hot zones)
        hot_zones = self._identify_hot_zones(points)

        # Identificar zonas frias (cold zones)
        cold_zones = self._identify_cold_zones(page, points)

        return HeatmapData(
            page=page,
            total_clicks=total_clicks,
            unique_users=unique_users,
            points=points,
            hot_zones=hot_zones,
            cold_zones=cold_zones,
        )

    def _generate_heatmap_points(self, page: str, event_type: str) -> List[HeatmapPoint]:
        """Gera pontos do heatmap (simulado)"""

        points = []

        # Definir zonas de interesse por página
        interest_zones = self._get_page_interest_zones(page)

        for zone in interest_zones:
            # Gerar pontos ao redor da zona
            num_points = zone["intensity"]

            for _ in range(num_points):
                # Adicionar variação aleatória
                x = zone["x"] + random.uniform(-20, 20)
                y = zone["y"] + random.uniform(-20, 20)

                points.append(
                    HeatmapPoint(
                        x=max(0, min(100, x)),  # % da largura
                        y=max(0, min(100, y)),  # % da altura
                        intensity=random.randint(zone["min_intensity"], zone["max_intensity"]),
                        page=page,
                        element=zone.get("element"),
                    )
                )

        return points

    def _get_page_interest_zones(self, page: str) -> List[Dict]:
        """Define zonas de interesse por página"""

        zones_by_page = {
            "/dashboard": [
                {
                    "x": 50,
                    "y": 20,
                    "element": "create_investigation_button",
                    "intensity": 150,
                    "min_intensity": 80,
                    "max_intensity": 100,
                },
                {
                    "x": 25,
                    "y": 40,
                    "element": "recent_investigations",
                    "intensity": 100,
                    "min_intensity": 50,
                    "max_intensity": 80,
                },
                {
                    "x": 75,
                    "y": 40,
                    "element": "statistics_widget",
                    "intensity": 80,
                    "min_intensity": 40,
                    "max_intensity": 70,
                },
                {
                    "x": 50,
                    "y": 60,
                    "element": "quick_actions",
                    "intensity": 120,
                    "min_intensity": 60,
                    "max_intensity": 90,
                },
            ],
            "/investigations": [
                {
                    "x": 80,
                    "y": 15,
                    "element": "new_button",
                    "intensity": 200,
                    "min_intensity": 90,
                    "max_intensity": 100,
                },
                {
                    "x": 50,
                    "y": 35,
                    "element": "investigation_list",
                    "intensity": 150,
                    "min_intensity": 70,
                    "max_intensity": 90,
                },
                {
                    "x": 20,
                    "y": 30,
                    "element": "filters",
                    "intensity": 60,
                    "min_intensity": 30,
                    "max_intensity": 60,
                },
            ],
            "/investigations/new": [
                {
                    "x": 50,
                    "y": 30,
                    "element": "cpf_cnpj_input",
                    "intensity": 180,
                    "min_intensity": 85,
                    "max_intensity": 100,
                },
                {
                    "x": 50,
                    "y": 50,
                    "element": "form_fields",
                    "intensity": 120,
                    "min_intensity": 60,
                    "max_intensity": 85,
                },
                {
                    "x": 70,
                    "y": 80,
                    "element": "submit_button",
                    "intensity": 160,
                    "min_intensity": 75,
                    "max_intensity": 95,
                },
            ],
            "/investigations/:id": [
                {
                    "x": 50,
                    "y": 25,
                    "element": "investigation_details",
                    "intensity": 140,
                    "min_intensity": 65,
                    "max_intensity": 90,
                },
                {
                    "x": 30,
                    "y": 50,
                    "element": "properties_tab",
                    "intensity": 110,
                    "min_intensity": 55,
                    "max_intensity": 80,
                },
                {
                    "x": 50,
                    "y": 50,
                    "element": "companies_tab",
                    "intensity": 100,
                    "min_intensity": 50,
                    "max_intensity": 75,
                },
                {
                    "x": 70,
                    "y": 50,
                    "element": "documents_tab",
                    "intensity": 80,
                    "min_intensity": 40,
                    "max_intensity": 70,
                },
                {
                    "x": 85,
                    "y": 20,
                    "element": "export_button",
                    "intensity": 90,
                    "min_intensity": 45,
                    "max_intensity": 75,
                },
            ],
            "/reports": [
                {
                    "x": 50,
                    "y": 30,
                    "element": "generate_report_button",
                    "intensity": 130,
                    "min_intensity": 60,
                    "max_intensity": 85,
                },
                {
                    "x": 50,
                    "y": 60,
                    "element": "report_preview",
                    "intensity": 100,
                    "min_intensity": 50,
                    "max_intensity": 75,
                },
            ],
            "/analytics": [
                {
                    "x": 30,
                    "y": 40,
                    "element": "metrics_dashboard",
                    "intensity": 110,
                    "min_intensity": 55,
                    "max_intensity": 80,
                },
                {
                    "x": 70,
                    "y": 40,
                    "element": "charts",
                    "intensity": 100,
                    "min_intensity": 50,
                    "max_intensity": 75,
                },
            ],
            "/settings": [
                {
                    "x": 30,
                    "y": 35,
                    "element": "profile_settings",
                    "intensity": 90,
                    "min_intensity": 45,
                    "max_intensity": 70,
                },
                {
                    "x": 70,
                    "y": 35,
                    "element": "notification_settings",
                    "intensity": 70,
                    "min_intensity": 35,
                    "max_intensity": 60,
                },
            ],
        }

        return zones_by_page.get(
            page,
            [
                {
                    "x": 50,
                    "y": 40,
                    "element": "main_content",
                    "intensity": 100,
                    "min_intensity": 50,
                    "max_intensity": 80,
                }
            ],
        )

    def _identify_hot_zones(self, points: List[HeatmapPoint]) -> List[Dict[str, Any]]:
        """Identifica zonas com muita interação"""

        # Agrupar pontos por elemento
        by_element = defaultdict(list)
        for point in points:
            if point.element:
                by_element[point.element].append(point)

        # Calcular intensidade média por elemento
        hot_zones = []
        for element, element_points in by_element.items():
            avg_intensity = sum(p.intensity for p in element_points) / len(element_points)

            if avg_intensity > 70:  # Threshold para "quente"
                hot_zones.append(
                    {
                        "element": element,
                        "click_count": len(element_points),
                        "average_intensity": round(avg_intensity, 2),
                        "center_x": round(
                            sum(p.x for p in element_points) / len(element_points), 2
                        ),
                        "center_y": round(
                            sum(p.y for p in element_points) / len(element_points), 2
                        ),
                    }
                )

        # Ordenar por intensidade
        hot_zones.sort(key=lambda x: x["average_intensity"], reverse=True)

        return hot_zones[:5]  # Top 5 hot zones

    def _identify_cold_zones(self, page: str, points: List[HeatmapPoint]) -> List[Dict[str, Any]]:
        """Identifica zonas com pouca interação"""

        # Elementos esperados mas com pouca interação
        interest_zones = self._get_page_interest_zones(page)

        clicked_elements = set(p.element for p in points if p.element)

        cold_zones = []
        for zone in interest_zones:
            element = zone.get("element")
            if element and element not in clicked_elements:
                cold_zones.append(
                    {
                        "element": element,
                        "expected_x": zone["x"],
                        "expected_y": zone["y"],
                        "click_count": 0,
                        "recommendation": f"Elemento '{element}' não está recebendo cliques. Melhorar visibilidade ou reposicionar.",
                    }
                )
            elif element:
                # Verificar se tem poucos cliques
                element_points = [p for p in points if p.element == element]
                if len(element_points) < zone["intensity"] * 0.3:  # Menos de 30% do esperado
                    cold_zones.append(
                        {
                            "element": element,
                            "expected_x": zone["x"],
                            "expected_y": zone["y"],
                            "click_count": len(element_points),
                            "recommendation": f"Elemento '{element}' com poucos cliques ({len(element_points)}). Considerar melhorias de UX.",
                        }
                    )

        return cold_zones

    def compare_heatmaps(
        self,
        page: str,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
    ) -> Dict[str, Any]:
        """Compara heatmaps de dois períodos"""

        heatmap1 = self.generate_heatmap(page, period1_start, period1_end)
        heatmap2 = self.generate_heatmap(page, period2_start, period2_end)

        # Comparar hot zones
        hot1_elements = set(hz["element"] for hz in heatmap1.hot_zones)
        hot2_elements = set(hz["element"] for hz in heatmap2.hot_zones)

        new_hot = hot2_elements - hot1_elements
        lost_hot = hot1_elements - hot2_elements

        return {
            "page": page,
            "period1": {
                "start": period1_start.isoformat(),
                "end": period1_end.isoformat(),
                "total_clicks": heatmap1.total_clicks,
                "hot_zones_count": len(heatmap1.hot_zones),
            },
            "period2": {
                "start": period2_start.isoformat(),
                "end": period2_end.isoformat(),
                "total_clicks": heatmap2.total_clicks,
                "hot_zones_count": len(heatmap2.hot_zones),
            },
            "changes": {
                "clicks_change": heatmap2.total_clicks - heatmap1.total_clicks,
                "clicks_change_pct": round(
                    (
                        (
                            (heatmap2.total_clicks - heatmap1.total_clicks)
                            / heatmap1.total_clicks
                            * 100
                        )
                        if heatmap1.total_clicks > 0
                        else 0
                    ),
                    2,
                ),
                "new_hot_zones": list(new_hot),
                "lost_hot_zones": list(lost_hot),
            },
        }


# ============================================================================
# 4. SESSION RECORDING ANALYTICS
# ============================================================================


class SessionRecordingAnalytics:
    """
    Gravação e Análise de Sessões

    Grava sessões de usuários para análise posterior.
    Identifica problemas de UX, erros e pontos de frustração.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_session_recording(self, session_id: str) -> SessionRecording:
        """
        Obtém gravação de uma sessão específica

        Args:
            session_id: ID da sessão

        Returns:
            Gravação completa da sessão
        """
        # Em produção, viria de storage (S3, etc) ou serviço de session recording
        # Aqui simulamos uma sessão realística

        return self._generate_mock_session(session_id)

    def _generate_mock_session(self, session_id: str) -> SessionRecording:
        """Gera sessão simulada para exemplo"""

        start_time = datetime.utcnow() - timedelta(hours=2)

        # Simular eventos de uma sessão típica
        events = [
            SessionEvent(
                timestamp=start_time,
                event_type="navigation",
                page="/dashboard",
                element=None,
                value=None,
            ),
            SessionEvent(
                timestamp=start_time + timedelta(seconds=5),
                event_type="click",
                page="/dashboard",
                element="create_investigation_button",
                x=50.0,
                y=20.0,
            ),
            SessionEvent(
                timestamp=start_time + timedelta(seconds=7),
                event_type="navigation",
                page="/investigations/new",
                element=None,
            ),
            SessionEvent(
                timestamp=start_time + timedelta(seconds=15),
                event_type="input",
                page="/investigations/new",
                element="cpf_input",
                value="***masked***",
            ),
            SessionEvent(
                timestamp=start_time + timedelta(seconds=20),
                event_type="click",
                page="/investigations/new",
                element="submit_button",
                x=70.0,
                y=80.0,
            ),
            SessionEvent(
                timestamp=start_time + timedelta(seconds=25),
                event_type="navigation",
                page="/investigations/123",
                element=None,
            ),
            SessionEvent(
                timestamp=start_time + timedelta(seconds=35),
                event_type="scroll",
                page="/investigations/123",
                y=30.0,
            ),
            SessionEvent(
                timestamp=start_time + timedelta(seconds=40),
                event_type="click",
                page="/investigations/123",
                element="properties_tab",
                x=30.0,
                y=50.0,
            ),
            SessionEvent(
                timestamp=start_time + timedelta(seconds=60),
                event_type="click",
                page="/investigations/123",
                element="export_button",
                x=85.0,
                y=20.0,
            ),
        ]

        end_time = events[-1].timestamp
        duration = (end_time - start_time).total_seconds()

        pages_visited = len(set(e.page for e in events if e.event_type == "navigation"))

        return SessionRecording(
            session_id=session_id,
            user_id=123,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            pages_visited=pages_visited,
            events_count=len(events),
            events=events,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            device_type="desktop",
            browser="Chrome",
            errors_encountered=0,
            completed_actions=["created_investigation", "viewed_properties", "exported_report"],
        )

    def analyze_session_patterns(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_duration_seconds: int = 30,
    ) -> Dict[str, Any]:
        """
        Analisa padrões de sessões

        Args:
            start_date: Data inicial
            end_date: Data final
            min_duration_seconds: Duração mínima para considerar

        Returns:
            Análise de padrões
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()

        # Simular análise de múltiplas sessões
        num_sessions = 500

        # Métricas agregadas (simuladas)
        avg_duration = 180  # 3 minutos
        avg_pages = 4
        avg_events = 25

        bounce_rate = 15.5  # % de sessões com apenas 1 página
        avg_actions_completed = 2.3
        error_rate = 5.2  # % de sessões com erros

        # Páginas mais visitadas
        popular_pages = [
            {"page": "/dashboard", "visits": 450, "avg_time_seconds": 45},
            {"page": "/investigations", "visits": 380, "avg_time_seconds": 90},
            {"page": "/investigations/new", "visits": 320, "avg_time_seconds": 120},
            {"page": "/investigations/:id", "visits": 280, "avg_time_seconds": 150},
            {"page": "/reports", "visits": 150, "avg_time_seconds": 60},
        ]

        # Ações mais comuns
        common_actions = [
            {"action": "created_investigation", "count": 320},
            {"action": "viewed_report", "count": 150},
            {"action": "exported_data", "count": 120},
            {"action": "shared_investigation", "count": 80},
        ]

        # Pontos de saída (onde usuários abandonam)
        exit_points = [
            {"page": "/investigations/new", "exit_count": 45, "exit_rate": 14.1},
            {"page": "/investigations/:id", "exit_count": 35, "exit_rate": 12.5},
            {"page": "/dashboard", "exit_count": 30, "exit_rate": 6.7},
        ]

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days,
            },
            "summary": {
                "total_sessions": num_sessions,
                "average_duration_seconds": avg_duration,
                "average_pages_per_session": avg_pages,
                "average_events_per_session": avg_events,
                "bounce_rate": bounce_rate,
                "average_actions_completed": avg_actions_completed,
                "sessions_with_errors": round(num_sessions * error_rate / 100),
                "error_rate": error_rate,
            },
            "popular_pages": popular_pages,
            "common_actions": common_actions,
            "exit_points": exit_points,
            "recommendations": self._generate_session_recommendations(
                bounce_rate, error_rate, exit_points
            ),
        }

    def _generate_session_recommendations(
        self, bounce_rate: float, error_rate: float, exit_points: List[Dict]
    ) -> List[str]:
        """Gera recomendações baseadas em padrões de sessão"""
        recommendations = []

        if bounce_rate > 20:
            recommendations.append(
                f"⚠️ Taxa de rejeição alta ({bounce_rate:.1f}%). "
                "Melhorar landing page e primeiras impressões."
            )

        if error_rate > 5:
            recommendations.append(
                f"🔴 {error_rate:.1f}% das sessões encontram erros. " "Priorizar correção de bugs."
            )

        # Analisar exit points
        high_exit = [ep for ep in exit_points if ep["exit_rate"] > 10]
        if high_exit:
            for ep in high_exit[:2]:
                recommendations.append(
                    f"🚪 Alta taxa de saída em {ep['page']} ({ep['exit_rate']:.1f}%). "
                    "Investigar motivos de abandono."
                )

        return recommendations if recommendations else ["✅ Padrões de sessão saudáveis."]


# ============================================================================
# 5. NPS (NET PROMOTER SCORE) ANALYTICS
# ============================================================================


class NPSAnalytics:
    """
    Net Promoter Score Analytics

    Coleta e analisa NPS para medir satisfação do cliente.
    Identifica promotores, passivos e detratores.
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_nps(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        segment: Optional[str] = None,
    ) -> NPSAnalysis:
        """
        Calcula NPS do período

        Args:
            start_date: Data inicial
            end_date: Data final
            segment: Segmento de usuários

        Returns:
            Análise completa de NPS
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()

        # Em produção, viria de tabela de respostas NPS
        # Aqui simulamos respostas realísticas

        responses = self._generate_nps_responses(start_date, end_date)

        total_responses = len(responses)

        if total_responses == 0:
            return NPSAnalysis(
                total_responses=0,
                detractors=0,
                passives=0,
                promoters=0,
                nps_score=0.0,
                average_score=0.0,
                response_rate=0.0,
                trend="stable",
                by_segment={},
            )

        # Categorizar respostas
        detractors = [r for r in responses if r.score <= 6]
        passives = [r for r in responses if 7 <= r.score <= 8]
        promoters = [r for r in responses if r.score >= 9]

        # Calcular NPS: (% promoters - % detractors)
        promoter_pct = len(promoters) / total_responses * 100
        detractor_pct = len(detractors) / total_responses * 100
        nps_score = promoter_pct - detractor_pct

        # Score médio
        average_score = sum(r.score for r in responses) / total_responses

        # Response rate (simulado)
        total_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        raw_rate = (total_responses / total_users * 100) if total_users > 0 else 0.0
        # Taxa de resposta como percentagem (nunca > 100 com dados simulados / denominador de utilizadores)
        response_rate = min(100.0, float(raw_rate))

        # Trend (comparar com período anterior)
        trend = self._calculate_nps_trend(nps_score)

        # NPS por segmento
        by_segment = self._calculate_nps_by_segment(responses)

        return NPSAnalysis(
            total_responses=total_responses,
            detractors=len(detractors),
            passives=len(passives),
            promoters=len(promoters),
            nps_score=round(nps_score, 2),
            average_score=round(average_score, 2),
            response_rate=round(response_rate, 2),
            trend=trend,
            by_segment=by_segment,
        )

    def _generate_nps_responses(
        self, start_date: datetime, end_date: datetime
    ) -> List[NPSResponse]:
        """Gera respostas NPS simuladas"""

        # Distribuição realística de NPS
        # Boa empresa: mais promotores que detratores
        score_distribution = [
            (9, 0.25),  # 25% dão nota 9
            (10, 0.20),  # 20% dão nota 10
            (8, 0.18),  # 18% dão nota 8
            (7, 0.12),  # 12% dão nota 7
            (6, 0.10),  # 10% dão nota 6
            (5, 0.07),  # 7% dão nota 5
            (4, 0.04),  # 4% dão nota 4
            (3, 0.02),  # 2% dão nota 3
            (2, 0.01),  # 1% dão nota 2
            (1, 0.005),  # 0.5% dão nota 1
            (0, 0.005),  # 0.5% dão nota 0
        ]

        responses = []
        num_responses = 150  # Simulando 150 respostas

        for i in range(num_responses):
            # Escolher score baseado na distribuição
            rand = random.random()
            cumulative = 0
            selected_score = 8

            for score, probability in score_distribution:
                cumulative += probability
                if rand <= cumulative:
                    selected_score = score
                    break

            # Categorizar
            if selected_score <= 6:
                category = "detractor"
            elif selected_score <= 8:
                category = "passive"
            else:
                category = "promoter"

            # Feedback opcional (mais comum para extremos)
            feedback = None
            if selected_score >= 9:
                feedback = random.choice(
                    [
                        "Excelente plataforma, muito útil!",
                        "Adorei a facilidade de usar",
                        "Recomendo fortemente",
                        None,
                        None,  # Nem todos deixam feedback
                    ]
                )
            elif selected_score <= 4:
                feedback = random.choice(
                    [
                        "Muitos bugs, precisa melhorar",
                        "Interface confusa",
                        "Suporte poderia ser melhor",
                        None,
                        None,
                    ]
                )

            created_at = start_date + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            )

            responses.append(
                NPSResponse(
                    user_id=i + 1,
                    score=selected_score,
                    category=category,
                    feedback=feedback,
                    created_at=created_at,
                )
            )

        return responses

    def _calculate_nps_trend(self, current_nps: float) -> str:
        """Calcula trend do NPS (simpl ficado)"""
        # Em produção, compararia com período anterior
        # Aqui simulamos
        if current_nps > 40:
            return "improving"
        elif current_nps > 20:
            return "stable"
        else:
            return "declining"

    def _calculate_nps_by_segment(self, responses: List[NPSResponse]) -> Dict[str, float]:
        """Calcula NPS por segmento de usuário"""

        # Simular segmentação
        # Em produção, juntaria com dados de usuário

        segments = {
            "new_users": responses[:50],
            "active_users": responses[50:120],
            "power_users": responses[120:],
        }

        nps_by_segment = {}

        for segment_name, segment_responses in segments.items():
            if not segment_responses:
                continue

            promoters = len([r for r in segment_responses if r.score >= 9])
            detractors = len([r for r in segment_responses if r.score <= 6])
            total = len(segment_responses)

            nps = ((promoters / total) - (detractors / total)) * 100 if total > 0 else 0
            nps_by_segment[segment_name] = round(nps, 2)

        return nps_by_segment

    def get_nps_feedback_analysis(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analisa feedback textual do NPS

        Returns:
            Análise de temas e sentimentos
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()

        responses = self._generate_nps_responses(start_date, end_date)

        # Filtrar respostas com feedback
        with_feedback = [r for r in responses if r.feedback]

        # Análise de sentimento simplificada
        promoter_feedback = [r.feedback for r in with_feedback if r.category == "promoter"]
        detractor_feedback = [r.feedback for r in with_feedback if r.category == "detractor"]

        # Temas comuns (simulado - em produção usaria NLP)
        promoter_themes = [
            {"theme": "Facilidade de uso", "mentions": 15},
            {"theme": "Funcionalidades úteis", "mentions": 12},
            {"theme": "Suporte excelente", "mentions": 8},
            {"theme": "Interface intuitiva", "mentions": 10},
        ]

        detractor_themes = [
            {"theme": "Bugs frequentes", "mentions": 5},
            {"theme": "Interface confusa", "mentions": 4},
            {"theme": "Falta de funcionalidades", "mentions": 3},
            {"theme": "Performance lenta", "mentions": 4},
        ]

        return {
            "total_feedback": len(with_feedback),
            "feedback_rate": (
                round(len(with_feedback) / len(responses) * 100, 2) if responses else 0
            ),
            "promoters": {"count": len(promoter_feedback), "common_themes": promoter_themes},
            "detractors": {"count": len(detractor_feedback), "common_themes": detractor_themes},
            "action_items": self._generate_nps_action_items(detractor_themes),
        }

    def _generate_nps_action_items(self, detractor_themes: List[Dict]) -> List[str]:
        """Gera ações baseadas em feedback de detratores"""
        action_items = []

        for theme in detractor_themes:
            if theme["mentions"] >= 4:
                action_items.append(
                    f"🔴 {theme['theme']}: {theme['mentions']} menções. Priorizar correção."
                )

        return action_items if action_items else ["✅ Poucos problemas reportados por detratores."]


# Exports
__all__ = ["HeatmapAnalytics", "SessionRecordingAnalytics", "NPSAnalytics"]
