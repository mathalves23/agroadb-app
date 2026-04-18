"""
Dados de demonstração após enriquecimento de investigação (MOCK_DEMO).

Desligado em produção; noutros ambientes só corre se
`ENABLE_INVESTIGATION_ENRICH_DEMO_SEED=true` na configuração.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.company import Company
from app.domain.property import Property


def enrich_demo_seed_enabled() -> bool:
    """Permite criar registos fictícios só fora de produção e com flag explícita."""
    env = (settings.ENVIRONMENT or "").strip().lower()
    if env in ("production", "prod"):
        return False
    return bool(settings.ENABLE_INVESTIGATION_ENRICH_DEMO_SEED)


async def maybe_seed_demo_properties_and_companies(
    db: AsyncSession,
    investigation_id: int,
    owner_label: str,
) -> None:
    """
    Se habilitado e a investigação não tiver propriedades/empresas, insere linhas MOCK_DEMO.
    Faz commit ao final de cada bloco (mantém o comportamento anterior do endpoint).
    """
    if not enrich_demo_seed_enabled():
        return

    result = await db.execute(select(Property).where(Property.investigation_id == investigation_id))
    existing_properties = result.scalars().all()
    if not existing_properties:
        for _ in range(random.randint(2, 4)):
            prop = Property(
                investigation_id=investigation_id,
                property_name=(
                    f"Fazenda {random.choice(['Esperança', 'Boa Vista', 'Santa Rita', 'Vale Verde'])} "
                    f"- Lote {random.randint(1, 50)}"
                ),
                car_number=f"BR-{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                area_hectares=round(random.uniform(100, 3000), 2),
                city=random.choice(["Uberlândia", "Rio Verde", "Dourados", "Sorriso"]),
                state=random.choice(["MG", "GO", "MS", "MT"]),
                owner_name=owner_label or "Proprietário não identificado",
                data_source="MOCK_DEMO",
            )
            db.add(prop)
        await db.commit()

    result = await db.execute(select(Company).where(Company.investigation_id == investigation_id))
    existing_companies = result.scalars().all()
    if not existing_companies:
        for _ in range(random.randint(1, 3)):
            company_name = (
                f"{random.choice(['Agropecuária', 'Fazendas', 'Empreendimentos'])} "
                f"{random.choice(['Vale Verde', 'Esperança', 'Santa Helena'])} Ltda"
            )
            company = Company(
                investigation_id=investigation_id,
                cnpj=(
                    f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}"
                    f"/0001-{random.randint(10, 99)}"
                ),
                corporate_name=company_name,
                trade_name=company_name,
                status=random.choice(["ATIVA", "ATIVA", "SUSPENSA"]),
                opening_date=datetime.utcnow() - timedelta(days=random.randint(365, 2000)),
                data_source="MOCK_DEMO",
            )
            db.add(company)
        await db.commit()
