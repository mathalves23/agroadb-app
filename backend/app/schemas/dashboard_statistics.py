"""Estatísticas agregadas para dashboards (sem dados sensíveis)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MonthInvestigationStat(BaseModel):
    month: str = Field(..., description="Rótulo curto, ex.: Jan/2026")
    count: int = 0
    completed: int = 0
    failed: int = 0


class ScraperPerformanceStat(BaseModel):
    name: str
    success: int = Field(..., ge=0, le=100, description="Percentual estimado de sucesso")
    failed: int = Field(..., ge=0, le=100, description="Complemento aproximado para visualização")


class StatePropertyStat(BaseModel):
    state: str
    count: int


class StatusSlice(BaseModel):
    name: str
    value: int
    color: str


class DashboardStatisticsResponse(BaseModel):
    investigations_by_month: list[MonthInvestigationStat]
    scrapers_performance: list[ScraperPerformanceStat]
    properties_by_state: list[StatePropertyStat]
    status_distribution: list[StatusSlice]
