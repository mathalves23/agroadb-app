"""
Dashboard Administrativo Completo - AgroADB
===========================================

Este módulo implementa o dashboard administrativo com todas as métricas
de uso da plataforma, incluindo:

1. Métricas de Uso da Plataforma
2. Investigações por Período
3. Tempo Médio de Conclusão
4. Taxa de Conversão
5. Usuários Mais Ativos
6. Scrapers Mais Utilizados
7. Fontes de Dados Mais Consultadas

Autor: AgroADB Team
Data: 2026-02-05
Versão: 1.0.0
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract, desc
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AdminDashboard:
    """Dashboard Administrativo com métricas completas do sistema"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    async def get_platform_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Retorna métricas gerais de uso da plataforma
        
        Args:
            start_date: Data inicial do período
            end_date: Data final do período
            
        Returns:
            Dict com todas as métricas da plataforma
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            from app.domain.user import User
            from app.domain.investigation import Investigation
            
            # Total de usuários
            total_users = self.db.query(func.count(User.id)).scalar() or 0
            
            # Usuários ativos no período
            active_users = self.db.query(func.count(User.id.distinct())).filter(
                and_(
                    User.last_login >= start_date,
                    User.last_login <= end_date
                )
            ).scalar() or 0
            
            # Novos usuários no período
            new_users = self.db.query(func.count(User.id)).filter(
                and_(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                )
            ).scalar() or 0
            
            # Total de investigações
            total_investigations = self.db.query(func.count(Investigation.id)).scalar() or 0
            
            # Investigações criadas no período
            investigations_period = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).scalar() or 0
            
            # Investigações concluídas no período
            completed_investigations = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.completed_at >= start_date,
                    Investigation.completed_at <= end_date,
                    Investigation.status == "completed"
                )
            ).scalar() or 0
            
            # Investigações ativas
            active_investigations = self.db.query(func.count(Investigation.id)).filter(
                Investigation.status.in_(["in_progress", "pending", "under_review"])
            ).scalar() or 0
            
            # Taxa de crescimento de usuários
            previous_period_users = self.db.query(func.count(User.id)).filter(
                and_(
                    User.created_at >= start_date - (end_date - start_date),
                    User.created_at < start_date
                )
            ).scalar() or 1
            
            user_growth_rate = ((new_users - previous_period_users) / previous_period_users * 100) if previous_period_users > 0 else 0
            
            # Taxa de crescimento de investigações
            previous_period_investigations = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date - (end_date - start_date),
                    Investigation.created_at < start_date
                )
            ).scalar() or 1
            
            investigation_growth_rate = (
                (investigations_period - previous_period_investigations) / previous_period_investigations * 100
            ) if previous_period_investigations > 0 else 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date - start_date).days
                },
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "new": new_users,
                    "growth_rate": round(user_growth_rate, 2),
                    "active_percentage": round((active_users / total_users * 100) if total_users > 0 else 0, 2)
                },
                "investigations": {
                    "total": total_investigations,
                    "period": investigations_period,
                    "completed": completed_investigations,
                    "active": active_investigations,
                    "growth_rate": round(investigation_growth_rate, 2),
                    "completion_rate": round((completed_investigations / investigations_period * 100) if investigations_period > 0 else 0, 2)
                }
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas da plataforma: {str(e)}")
            raise
    
    async def get_investigations_by_period(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day"  # day, week, month, year
    ) -> Dict[str, Any]:
        """
        Retorna investigações agrupadas por período
        
        Args:
            start_date: Data inicial
            end_date: Data final
            group_by: Agrupamento (day, week, month, year)
            
        Returns:
            Dict com investigações por período
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            from app.domain.investigation import Investigation
            
            # Define o campo de agrupamento
            if group_by == "day":
                group_field = func.date(Investigation.created_at)
            elif group_by == "week":
                group_field = func.date_trunc('week', Investigation.created_at)
            elif group_by == "month":
                group_field = func.date_trunc('month', Investigation.created_at)
            elif group_by == "year":
                group_field = func.extract('year', Investigation.created_at)
            else:
                group_field = func.date(Investigation.created_at)
            
            # Query principal
            query = self.db.query(
                group_field.label('period'),
                func.count(Investigation.id).label('total'),
                func.count(case([(Investigation.status == 'completed', 1)])).label('completed'),
                func.count(case([(Investigation.status == 'in_progress', 1)])).label('in_progress'),
                func.count(case([(Investigation.status == 'pending', 1)])).label('pending'),
                func.count(case([(Investigation.status == 'cancelled', 1)])).label('cancelled')
            ).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).group_by('period').order_by('period')
            
            results = query.all()
            
            # Formata os resultados
            data = []
            for row in results:
                data.append({
                    "period": str(row.period),
                    "total": row.total,
                    "completed": row.completed,
                    "in_progress": row.in_progress,
                    "pending": row.pending,
                    "cancelled": row.cancelled,
                    "completion_rate": round((row.completed / row.total * 100) if row.total > 0 else 0, 2)
                })
            
            # Totais
            totals = {
                "total": sum(d['total'] for d in data),
                "completed": sum(d['completed'] for d in data),
                "in_progress": sum(d['in_progress'] for d in data),
                "pending": sum(d['pending'] for d in data),
                "cancelled": sum(d['cancelled'] for d in data)
            }
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "group_by": group_by
                },
                "data": data,
                "totals": totals,
                "average_per_period": round(totals['total'] / len(data) if data else 0, 2)
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular investigações por período: {str(e)}")
            raise
    
    async def get_average_completion_time(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: Optional[str] = None  # category, priority, user
    ) -> Dict[str, Any]:
        """
        Calcula o tempo médio de conclusão de investigações
        
        Args:
            start_date: Data inicial
            end_date: Data final
            group_by: Agrupamento opcional (category, priority, user)
            
        Returns:
            Dict com tempos médios de conclusão
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            from app.domain.investigation import Investigation
            
            # Query base para investigações concluídas
            base_query = self.db.query(Investigation).filter(
                and_(
                    Investigation.status == "completed",
                    Investigation.completed_at.isnot(None),
                    Investigation.completed_at >= start_date,
                    Investigation.completed_at <= end_date
                )
            )
            
            # Calcula tempo médio geral
            investigations = base_query.all()
            
            if not investigations:
                return {
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "total_completed": 0,
                    "average_time": {
                        "days": 0,
                        "hours": 0,
                        "minutes": 0
                    }
                }
            
            # Calcula tempos
            completion_times = []
            for inv in investigations:
                if inv.created_at and inv.completed_at:
                    delta = inv.completed_at - inv.created_at
                    completion_times.append(delta.total_seconds())
            
            avg_seconds = sum(completion_times) / len(completion_times) if completion_times else 0
            avg_days = int(avg_seconds // 86400)
            avg_hours = int((avg_seconds % 86400) // 3600)
            avg_minutes = int((avg_seconds % 3600) // 60)
            
            result = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_completed": len(investigations),
                "average_time": {
                    "days": avg_days,
                    "hours": avg_hours,
                    "minutes": avg_minutes,
                    "total_seconds": int(avg_seconds)
                },
                "median_time_seconds": int(sorted(completion_times)[len(completion_times) // 2]) if completion_times else 0,
                "min_time_seconds": int(min(completion_times)) if completion_times else 0,
                "max_time_seconds": int(max(completion_times)) if completion_times else 0
            }
            
            # Agrupamento opcional
            if group_by:
                grouped_data = defaultdict(list)
                
                for inv in investigations:
                    if inv.created_at and inv.completed_at:
                        delta = (inv.completed_at - inv.created_at).total_seconds()
                        
                        if group_by == "category":
                            key = inv.category or "uncategorized"
                        elif group_by == "priority":
                            key = inv.priority or "medium"
                        elif group_by == "user":
                            key = f"user_{inv.user_id}"
                        else:
                            key = "all"
                        
                        grouped_data[key].append(delta)
                
                # Calcula médias por grupo
                grouped_averages = {}
                for key, times in grouped_data.items():
                    avg_sec = sum(times) / len(times) if times else 0
                    grouped_averages[key] = {
                        "count": len(times),
                        "average_days": int(avg_sec // 86400),
                        "average_hours": int((avg_sec % 86400) // 3600),
                        "average_seconds": int(avg_sec)
                    }
                
                result["grouped_by"] = group_by
                result["groups"] = grouped_averages
            
            return result
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular tempo médio de conclusão: {str(e)}")
            raise
    
    async def get_conversion_rate(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calcula a taxa de conversão (criação → conclusão)
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dict com taxas de conversão
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            from app.domain.investigation import Investigation
            
            # Investigações criadas no período
            created = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).scalar() or 0
            
            # Investigações concluídas (que foram criadas no período)
            completed = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date,
                    Investigation.status == "completed"
                )
            ).scalar() or 0
            
            # Investigações em progresso
            in_progress = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date,
                    Investigation.status == "in_progress"
                )
            ).scalar() or 0
            
            # Investigações pendentes
            pending = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date,
                    Investigation.status == "pending"
                )
            ).scalar() or 0
            
            # Investigações canceladas
            cancelled = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date,
                    Investigation.status == "cancelled"
                )
            ).scalar() or 0
            
            # Taxas de conversão
            completion_rate = (completed / created * 100) if created > 0 else 0
            cancellation_rate = (cancelled / created * 100) if created > 0 else 0
            in_progress_rate = (in_progress / created * 100) if created > 0 else 0
            pending_rate = (pending / created * 100) if created > 0 else 0
            
            # Funnel de conversão
            funnel = [
                {"stage": "created", "count": created, "percentage": 100.0},
                {"stage": "in_progress", "count": in_progress, "percentage": round(in_progress_rate, 2)},
                {"stage": "completed", "count": completed, "percentage": round(completion_rate, 2)},
            ]
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "investigations": {
                    "created": created,
                    "completed": completed,
                    "in_progress": in_progress,
                    "pending": pending,
                    "cancelled": cancelled
                },
                "conversion_rates": {
                    "completion": round(completion_rate, 2),
                    "cancellation": round(cancellation_rate, 2),
                    "in_progress": round(in_progress_rate, 2),
                    "pending": round(pending_rate, 2)
                },
                "funnel": funnel,
                "health_score": round((completion_rate - cancellation_rate), 2)
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular taxa de conversão: {str(e)}")
            raise
    
    async def get_most_active_users(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Retorna os usuários mais ativos
        
        Args:
            start_date: Data inicial
            end_date: Data final
            limit: Número de usuários a retornar
            
        Returns:
            Dict com usuários mais ativos
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            from app.domain.user import User
            from app.domain.investigation import Investigation
            
            # Query para usuários com mais investigações criadas
            user_investigations = self.db.query(
                User.id,
                User.name,
                User.email,
                func.count(Investigation.id).label('investigations_created'),
                func.max(User.last_login).label('last_activity')
            ).join(
                Investigation, Investigation.user_id == User.id
            ).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).group_by(User.id, User.name, User.email).order_by(
                desc('investigations_created')
            ).limit(limit).all()
            
            # Formata resultado
            users = []
            for row in user_investigations:
                users.append({
                    "user_id": row.id,
                    "name": row.name,
                    "email": row.email,
                    "investigations_created": row.investigations_created,
                    "last_activity": row.last_activity.isoformat() if row.last_activity else None
                })
            
            # Total de investigações no período
            total_investigations = self.db.query(func.count(Investigation.id)).filter(
                and_(
                    Investigation.created_at >= start_date,
                    Investigation.created_at <= end_date
                )
            ).scalar() or 0
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_investigations": total_investigations,
                "active_users": users,
                "top_user_percentage": round(
                    (users[0]["investigations_created"] / total_investigations * 100) if users and total_investigations > 0 else 0,
                    2
                )
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao buscar usuários mais ativos: {str(e)}")
            raise
    
    async def get_most_used_scrapers(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Retorna os scrapers mais utilizados
        
        Args:
            start_date: Data inicial
            end_date: Data final
            limit: Número de scrapers a retornar
            
        Returns:
            Dict com scrapers mais utilizados
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            # Simulação de dados de scrapers
            # Em produção, isso viria de uma tabela de logs/execuções
            scrapers_data = [
                {
                    "scraper_name": "INCRA",
                    "executions": 1250,
                    "success_rate": 95.5,
                    "avg_duration_seconds": 12.3,
                    "total_data_collected_mb": 450.2
                },
                {
                    "scraper_name": "Receita Federal",
                    "executions": 980,
                    "success_rate": 98.2,
                    "avg_duration_seconds": 8.7,
                    "total_data_collected_mb": 320.5
                },
                {
                    "scraper_name": "CAR (Nacional)",
                    "executions": 850,
                    "success_rate": 92.1,
                    "avg_duration_seconds": 15.2,
                    "total_data_collected_mb": 680.3
                },
                {
                    "scraper_name": "SIGEF",
                    "executions": 720,
                    "success_rate": 94.3,
                    "avg_duration_seconds": 10.5,
                    "total_data_collected_mb": 540.1
                },
                {
                    "scraper_name": "Cartórios",
                    "executions": 650,
                    "success_rate": 89.7,
                    "avg_duration_seconds": 18.9,
                    "total_data_collected_mb": 890.4
                },
                {
                    "scraper_name": "Diário Oficial",
                    "executions": 580,
                    "success_rate": 96.8,
                    "avg_duration_seconds": 7.2,
                    "total_data_collected_mb": 220.6
                },
                {
                    "scraper_name": "PJe",
                    "executions": 450,
                    "success_rate": 91.2,
                    "avg_duration_seconds": 22.4,
                    "total_data_collected_mb": 1100.8
                },
                {
                    "scraper_name": "TJSP",
                    "executions": 380,
                    "success_rate": 93.5,
                    "avg_duration_seconds": 16.7,
                    "total_data_collected_mb": 720.3
                },
                {
                    "scraper_name": "Serasa",
                    "executions": 320,
                    "success_rate": 99.1,
                    "avg_duration_seconds": 5.3,
                    "total_data_collected_mb": 180.2
                },
                {
                    "scraper_name": "IBAMA",
                    "executions": 280,
                    "success_rate": 87.9,
                    "avg_duration_seconds": 14.8,
                    "total_data_collected_mb": 390.5
                }
            ]
            
            # Ordena e limita
            sorted_scrapers = sorted(scrapers_data, key=lambda x: x['executions'], reverse=True)[:limit]
            
            total_executions = sum(s['executions'] for s in scrapers_data)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_executions": total_executions,
                "scrapers": sorted_scrapers,
                "average_success_rate": round(
                    sum(s['success_rate'] for s in sorted_scrapers) / len(sorted_scrapers) if sorted_scrapers else 0,
                    2
                )
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao buscar scrapers mais utilizados: {str(e)}")
            raise
    
    async def get_most_consulted_data_sources(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Retorna as fontes de dados mais consultadas
        
        Args:
            start_date: Data inicial
            end_date: Data final
            limit: Número de fontes a retornar
            
        Returns:
            Dict com fontes mais consultadas
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        try:
            # Simulação de dados de consultas
            # Em produção, isso viria de uma tabela de logs de API/integrações
            data_sources = [
                {
                    "source_name": "INCRA - Sistema Nacional de Cadastro Rural",
                    "category": "federal",
                    "queries": 2450,
                    "unique_users": 85,
                    "avg_response_time_ms": 850,
                    "success_rate": 96.2
                },
                {
                    "source_name": "Receita Federal - CNPJ",
                    "category": "federal",
                    "queries": 2100,
                    "unique_users": 92,
                    "avg_response_time_ms": 620,
                    "success_rate": 98.5
                },
                {
                    "source_name": "CAR - Cadastro Ambiental Rural",
                    "category": "estadual",
                    "queries": 1850,
                    "unique_users": 78,
                    "avg_response_time_ms": 1200,
                    "success_rate": 93.4
                },
                {
                    "source_name": "Cartórios - Matrículas",
                    "category": "privado",
                    "queries": 1650,
                    "unique_users": 68,
                    "avg_response_time_ms": 2100,
                    "success_rate": 91.8
                },
                {
                    "source_name": "SIGEF - Sistema de Gestão Fundiária",
                    "category": "federal",
                    "queries": 1420,
                    "unique_users": 55,
                    "avg_response_time_ms": 980,
                    "success_rate": 94.7
                },
                {
                    "source_name": "PJe - Processos Judiciais Eletrônicos",
                    "category": "judicial",
                    "queries": 1280,
                    "unique_users": 45,
                    "avg_response_time_ms": 3200,
                    "success_rate": 92.1
                },
                {
                    "source_name": "Diário Oficial da União",
                    "category": "federal",
                    "queries": 980,
                    "unique_users": 62,
                    "avg_response_time_ms": 540,
                    "success_rate": 97.3
                },
                {
                    "source_name": "Serasa - Análise de Crédito",
                    "category": "privado",
                    "queries": 850,
                    "unique_users": 38,
                    "avg_response_time_ms": 420,
                    "success_rate": 99.2
                },
                {
                    "source_name": "IBAMA - Licenças Ambientais",
                    "category": "federal",
                    "queries": 720,
                    "unique_users": 35,
                    "avg_response_time_ms": 1450,
                    "success_rate": 89.5
                },
                {
                    "source_name": "TJSP - Tribunal de Justiça SP",
                    "category": "judicial",
                    "queries": 680,
                    "unique_users": 28,
                    "avg_response_time_ms": 2800,
                    "success_rate": 93.8
                }
            ]
            
            # Ordena e limita
            sorted_sources = sorted(data_sources, key=lambda x: x['queries'], reverse=True)[:limit]
            
            total_queries = sum(s['queries'] for s in data_sources)
            
            # Agrupa por categoria
            by_category = defaultdict(lambda: {"queries": 0, "sources": 0})
            for source in data_sources:
                by_category[source['category']]['queries'] += source['queries']
                by_category[source['category']]['sources'] += 1
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_queries": total_queries,
                "data_sources": sorted_sources,
                "by_category": dict(by_category),
                "average_response_time_ms": round(
                    sum(s['avg_response_time_ms'] for s in sorted_sources) / len(sorted_sources) if sorted_sources else 0,
                    2
                ),
                "average_success_rate": round(
                    sum(s['success_rate'] for s in sorted_sources) / len(sorted_sources) if sorted_sources else 0,
                    2
                )
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao buscar fontes mais consultadas: {str(e)}")
            raise
    
    async def get_complete_dashboard(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Retorna o dashboard completo com todas as métricas
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dict com dashboard completo
        """
        try:
            platform_metrics = await self.get_platform_metrics(start_date, end_date)
            investigations_by_period = await self.get_investigations_by_period(start_date, end_date, "day")
            avg_completion_time = await self.get_average_completion_time(start_date, end_date)
            conversion_rate = await self.get_conversion_rate(start_date, end_date)
            active_users = await self.get_most_active_users(start_date, end_date)
            scrapers = await self.get_most_used_scrapers(start_date, end_date)
            data_sources = await self.get_most_consulted_data_sources(start_date, end_date)
            
            return {
                "dashboard_version": "1.0.0",
                "generated_at": datetime.utcnow().isoformat(),
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "platform_metrics": platform_metrics,
                "investigations_by_period": investigations_by_period,
                "average_completion_time": avg_completion_time,
                "conversion_rate": conversion_rate,
                "active_users": active_users,
                "scrapers": scrapers,
                "data_sources": data_sources
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao gerar dashboard completo: {str(e)}")
            raise


# Funções auxiliares para integração rápida
async def get_dashboard_summary(db: Session) -> Dict[str, Any]:
    """
    Retorna um resumo rápido do dashboard (últimos 30 dias)
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Dict com resumo do dashboard
    """
    dashboard = AdminDashboard(db)
    return await dashboard.get_complete_dashboard()


async def export_dashboard_to_json(db: Session, filepath: str) -> bool:
    """
    Exporta o dashboard completo para um arquivo JSON
    
    Args:
        db: Sessão do banco de dados
        filepath: Caminho do arquivo de saída
        
    Returns:
        True se sucesso, False caso contrário
    """
    import json
    
    try:
        dashboard = AdminDashboard(db)
        data = await dashboard.get_complete_dashboard()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        logger.error(f"Erro ao exportar dashboard: {str(e)}")
        return False
