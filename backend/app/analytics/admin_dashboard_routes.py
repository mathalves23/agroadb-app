"""
Rotas da API - Dashboard Administrativo
========================================

Este módulo implementa os endpoints da API REST para o dashboard administrativo.

Endpoints disponíveis:
- GET /admin/dashboard/metrics - Métricas gerais da plataforma
- GET /admin/dashboard/investigations - Investigações por período
- GET /admin/dashboard/completion-time - Tempo médio de conclusão
- GET /admin/dashboard/conversion - Taxa de conversão
- GET /admin/dashboard/active-users - Usuários mais ativos
- GET /admin/dashboard/scrapers - Scrapers mais utilizados
- GET /admin/dashboard/data-sources - Fontes de dados mais consultadas
- GET /admin/dashboard/complete - Dashboard completo

Autor: AgroADB Team
Data: 2026-02-05
Versão: 1.0.0
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.deps import get_current_user, require_admin
from app.analytics.admin_dashboard import AdminDashboard
from app.domain.user import User

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])


@router.get("/metrics")
async def get_platform_metrics(
    start_date: Optional[datetime] = Query(None, description="Data inicial (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Data final (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Retorna métricas gerais de uso da plataforma
    
    **Requer:** Permissões de administrador
    
    **Retorna:**
    - Total de usuários, ativos, novos
    - Total de investigações
    - Taxas de crescimento
    """
    try:
        dashboard = AdminDashboard(db)
        return await dashboard.get_platform_metrics(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar métricas: {str(e)}")


@router.get("/investigations")
async def get_investigations_by_period(
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    group_by: str = Query("day", regex="^(day|week|month|year)$", description="Agrupamento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Retorna investigações agrupadas por período
    
    **Parâmetros:**
    - group_by: day, week, month ou year
    
    **Requer:** Permissões de administrador
    """
    try:
        dashboard = AdminDashboard(db)
        return await dashboard.get_investigations_by_period(start_date, end_date, group_by)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar investigações: {str(e)}")


@router.get("/completion-time")
async def get_average_completion_time(
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    group_by: Optional[str] = Query(None, regex="^(category|priority|user)$", description="Agrupamento opcional"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Calcula o tempo médio de conclusão de investigações
    
    **Parâmetros:**
    - group_by (opcional): category, priority ou user
    
    **Requer:** Permissões de administrador
    """
    try:
        dashboard = AdminDashboard(db)
        return await dashboard.get_average_completion_time(start_date, end_date, group_by)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular tempo de conclusão: {str(e)}")


@router.get("/conversion")
async def get_conversion_rate(
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Calcula a taxa de conversão (criação → conclusão)
    
    **Retorna:**
    - Taxas de conclusão, cancelamento
    - Funnel de conversão
    - Health score
    
    **Requer:** Permissões de administrador
    """
    try:
        dashboard = AdminDashboard(db)
        return await dashboard.get_conversion_rate(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular conversão: {str(e)}")


@router.get("/active-users")
async def get_most_active_users(
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    limit: int = Query(10, ge=1, le=100, description="Número de usuários"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Retorna os usuários mais ativos
    
    **Parâmetros:**
    - limit: Quantidade de usuários (1-100)
    
    **Requer:** Permissões de administrador
    """
    try:
        dashboard = AdminDashboard(db)
        return await dashboard.get_most_active_users(start_date, end_date, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários ativos: {str(e)}")


@router.get("/scrapers")
async def get_most_used_scrapers(
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    limit: int = Query(10, ge=1, le=50, description="Número de scrapers"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Retorna os scrapers mais utilizados
    
    **Parâmetros:**
    - limit: Quantidade de scrapers (1-50)
    
    **Requer:** Permissões de administrador
    """
    try:
        dashboard = AdminDashboard(db)
        return await dashboard.get_most_used_scrapers(start_date, end_date, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar scrapers: {str(e)}")


@router.get("/data-sources")
async def get_most_consulted_data_sources(
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    limit: int = Query(10, ge=1, le=50, description="Número de fontes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Retorna as fontes de dados mais consultadas
    
    **Parâmetros:**
    - limit: Quantidade de fontes (1-50)
    
    **Requer:** Permissões de administrador
    """
    try:
        dashboard = AdminDashboard(db)
        return await dashboard.get_most_consulted_data_sources(start_date, end_date, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fontes: {str(e)}")


@router.get("/complete")
async def get_complete_dashboard(
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Retorna o dashboard completo com todas as métricas
    
    **Inclui:**
    - Métricas da plataforma
    - Investigações por período
    - Tempo médio de conclusão
    - Taxa de conversão
    - Usuários mais ativos
    - Scrapers mais utilizados
    - Fontes mais consultadas
    
    **Requer:** Permissões de administrador
    
    **Nota:** Este endpoint pode demorar alguns segundos para executar
    """
    try:
        dashboard = AdminDashboard(db)
        return await dashboard.get_complete_dashboard(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard: {str(e)}")


@router.get("/export")
async def export_dashboard(
    format: str = Query("json", regex="^(json|csv)$", description="Formato de exportação"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Exporta o dashboard completo em formato JSON ou CSV
    
    **Parâmetros:**
    - format: json ou csv
    
    **Requer:** Permissões de administrador
    """
    from fastapi.responses import StreamingResponse
    import json
    import io
    
    try:
        dashboard = AdminDashboard(db)
        data = await dashboard.get_complete_dashboard(start_date, end_date)
        
        if format == "json":
            content = json.dumps(data, indent=2, ensure_ascii=False)
            media_type = "application/json"
            filename = f"dashboard_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            # CSV simplificado (apenas métricas principais)
            import csv
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Cabeçalhos
            writer.writerow(["Métrica", "Valor"])
            
            # Métricas de usuários
            writer.writerow(["Total de Usuários", data["platform_metrics"]["users"]["total"]])
            writer.writerow(["Usuários Ativos", data["platform_metrics"]["users"]["active"]])
            writer.writerow(["Novos Usuários", data["platform_metrics"]["users"]["new"]])
            
            # Métricas de investigações
            writer.writerow(["Total de Investigações", data["platform_metrics"]["investigations"]["total"]])
            writer.writerow(["Investigações Concluídas", data["platform_metrics"]["investigations"]["completed"]])
            writer.writerow(["Taxa de Conclusão (%)", data["conversion_rate"]["conversion_rates"]["completion"]])
            
            content = output.getvalue()
            media_type = "text/csv"
            filename = f"dashboard_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.BytesIO(content.encode('utf-8')),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar dashboard: {str(e)}")
