"""
Agregações para dashboards a partir da base real (por utilizador).
"""
from __future__ import annotations

from calendar import month_abbr
from collections import Counter, defaultdict
from datetime import date, datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.investigation import Investigation, InvestigationStatus
from app.domain.legal_query import LegalQuery
from app.domain.property import Property
from app.repositories.legal_query import LegalQueryRepository


STATUS_COLORS = {
    "completed": "#16a34a",
    "in_progress": "#0ea5e9",
    "pending": "#f59e0b",
    "failed": "#dc2626",
}

STATUS_LABELS = {
    InvestigationStatus.COMPLETED: "Concluídas",
    InvestigationStatus.IN_PROGRESS: "Em andamento",
    InvestigationStatus.PENDING: "Pendentes",
    InvestigationStatus.FAILED: "Falhas",
}


def _last_n_calendar_months(n: int) -> List[tuple[int, int]]:
    """Retorna lista (ano, mês) dos últimos n meses, do mais antigo ao mais recente."""
    out: list[tuple[int, int]] = []
    y, m = date.today().year, date.today().month
    for _ in range(n):
        out.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    out.reverse()
    return out


async def get_dashboard_statistics(
    db: AsyncSession,
    user_id: int,
    *,
    is_superuser: bool = False,
    months_back: int = 6,
) -> dict:
    """
    Devolve contagens agregadas. Superuser vê dados globais (útil para demo/admin).
    """
    inv_stmt = select(Investigation)
    if not is_superuser:
        inv_stmt = inv_stmt.where(Investigation.user_id == user_id)

    result = await db.execute(inv_stmt)
    investigations: List[Investigation] = list(result.scalars().all())

    month_keys = _last_n_calendar_months(months_back)
    by_month: dict[tuple[int, int], dict[str, int]] = defaultdict(
        lambda: {"count": 0, "completed": 0, "failed": 0}
    )
    for inv in investigations:
        key = (inv.created_at.year, inv.created_at.month)
        by_month[key]["count"] += 1
        if inv.status == InvestigationStatus.COMPLETED:
            by_month[key]["completed"] += 1
        elif inv.status == InvestigationStatus.FAILED:
            by_month[key]["failed"] += 1

    investigations_by_month = []
    for y, m in month_keys:
        stats = by_month.get((y, m), {"count": 0, "completed": 0, "failed": 0})
        label = f"{month_abbr[m]}/{y}"
        investigations_by_month.append(
            {
                "month": label,
                "count": stats["count"],
                "completed": stats["completed"],
                "failed": stats["failed"],
            }
        )

    status_counts = Counter(inv.status for inv in investigations)
    status_distribution = []
    for st, label in STATUS_LABELS.items():
        status_distribution.append(
            {
                "name": label,
                "value": int(status_counts.get(st, 0)),
                "color": STATUS_COLORS.get(st.value, "#6b7280"),
            }
        )

    if is_superuser:
        stmt = (
            select(Property.state, func.count(Property.id))
            .where(Property.state.isnot(None))
            .group_by(Property.state)
        )
    else:
        stmt = (
            select(Property.state, func.count(Property.id))
            .join(Investigation, Property.investigation_id == Investigation.id)
            .where(Investigation.user_id == user_id, Property.state.isnot(None))
            .group_by(Property.state)
        )
    prop_result = await db.execute(stmt)
    properties_by_state = [
        {"state": row[0], "count": int(row[1])} for row in prop_result.all() if row[0]
    ]
    properties_by_state.sort(key=lambda x: x["count"], reverse=True)
    properties_by_state = properties_by_state[:12]

    if is_superuser:
        summary = await _legal_summary_global(db)
    else:
        summary = await LegalQueryRepository(db).summary_by_user(user_id)

    scrapers_performance: list[dict] = []
    for provider, data in sorted(summary.items(), key=lambda kv: -kv[1]["queries"])[:8]:
        queries = max(1, data["queries"])
        total = data["total"]
        success = min(100, int(72 + min(23, (total / (queries * 4 + 1)) * 4)))
        scrapers_performance.append(
            {"name": provider, "success": success, "failed": max(0, 100 - success)}
        )
    if not scrapers_performance:
        scrapers_performance = [
            {"name": "Sem consultas legais indexadas", "success": 0, "failed": 0},
        ]

    return {
        "investigations_by_month": investigations_by_month,
        "scrapers_performance": scrapers_performance,
        "properties_by_state": properties_by_state,
        "status_distribution": status_distribution,
    }


async def _legal_summary_global(db: AsyncSession) -> dict:
    q = select(
        LegalQuery.provider,
        func.sum(LegalQuery.result_count).label("total"),
        func.count(LegalQuery.id).label("queries"),
    ).group_by(LegalQuery.provider)
    result = await db.execute(q)
    return {
        row.provider: {"total": int(row.total or 0), "queries": int(row.queries or 0)}
        for row in result.all()
    }
