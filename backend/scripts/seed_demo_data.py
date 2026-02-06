"""
Script para criar dados completos de demonstração
Cria múltiplos usuários, investigações, propriedades, empresas, notificações, etc.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.domain.user import User
from app.domain.user_setting import UserSetting  # noqa: F401
from app.domain.notification import Notification, NotificationType, NotificationPriority
from app.domain.investigation import Investigation, InvestigationStatus
from app.domain.property import Property
from app.domain.company import Company
from app.domain.lease_contract import LeaseContract
from app.domain.legal_query import LegalQuery
from app.services.collaboration import InvestigationComment, InvestigationChangeLog


# Dados de exemplo
DEMO_USERS = [
    {
        "email": "demo@agroadb.com",
        "username": "demo",
        "password": "demo123",
        "full_name": "Usuário Demo",
        "organization": "AgroADB Demo",
    },
    {
        "email": "maria.silva@agroadb.com",
        "username": "maria.silva",
        "password": "demo123",
        "full_name": "Maria Silva Santos",
        "organization": "Silva & Associados",
    },
    {
        "email": "joao.santos@agroadb.com",
        "username": "joao.santos",
        "password": "demo123",
        "full_name": "João Santos Oliveira",
        "organization": "Santos Consultoria Rural",
    },
]

INVESTIGATIONS_DATA = [
    {
        "target_name": "Fazenda Santa Helena",
        "target_cpf_cnpj": None,
        "description": "Investigação patrimonial completa - suspeita de fraude em licitação",
        "priority": 5,
        "status": InvestigationStatus.IN_PROGRESS,
    },
    {
        "target_name": "Agropecuária Vale Verde Ltda",
        "target_cpf_cnpj": None,
        "description": "Análise de vínculos societários e propriedades rurais",
        "priority": 4,
        "status": InvestigationStatus.IN_PROGRESS,
    },
    {
        "target_name": "José Carlos Mendes",
        "target_cpf_cnpj": None,
        "description": "Levantamento patrimonial - processo trabalhista",
        "priority": 3,
        "status": InvestigationStatus.COMPLETED,
    },
    {
        "target_name": "Fazenda Esperança",
        "target_cpf_cnpj": None,
        "description": "Verificação de regularização ambiental e fundiária",
        "priority": 3,
        "status": InvestigationStatus.PENDING,
    },
]


async def create_demo_data():
    """Cria dados completos de demonstração"""
    async with AsyncSessionLocal() as db:
        print("=" * 70)
        print("  🎬 CRIANDO DADOS DE DEMONSTRAÇÃO - AgroADB")
        print("=" * 70)
        print()
        
        # 1. Criar usuários
        print("👥 Criando usuários demo...")
        users = []
        for user_data in DEMO_USERS:
            result = await db.execute(
                select(User).where(User.email == user_data["email"])
            )
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    full_name=user_data["full_name"],
                    organization=user_data["organization"],
                    hashed_password=get_password_hash(user_data["password"]),
                    is_active=True,
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                print(f"   ✅ Criado: {user.email}")
            else:
                print(f"   ℹ️  Já existe: {user.email}")
            
            users.append(user)
        
        print(f"   ✅ {len(users)} usuários disponíveis\n")
        
        # 2. Criar investigações para cada usuário
        print("🔍 Criando investigações...")
        total_investigations = 0
        
        for user in users:
            num_investigations = random.randint(2, 4)
            
            for i in range(num_investigations):
                inv_data = random.choice(INVESTIGATIONS_DATA).copy()
                inv_data["target_name"] = f"{inv_data['target_name']} #{random.randint(100, 999)}"
                
                investigation = Investigation(
                    user_id=user.id,
                    **inv_data,
                    properties_found=random.randint(3, 15),
                    companies_found=random.randint(1, 8),
                    lease_contracts_found=random.randint(0, 10),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                )
                db.add(investigation)
                total_investigations += 1
            
            await db.commit()
        
        print(f"   ✅ {total_investigations} investigações criadas\n")
        
        # 3. Criar propriedades para investigações
        print("🏞️  Criando propriedades...")
        result = await db.execute(select(Investigation))
        investigations = result.scalars().all()
        
        total_properties = 0
        for investigation in investigations:
            num_props = random.randint(2, 5)
            
            for i in range(num_props):
                property_data = Property(
                    investigation_id=investigation.id,
                    name=f"Fazenda {random.choice(['São José', 'Santa Rita', 'Boa Vista', 'Esperança', 'Vale Verde'])} - Lote {random.randint(1, 50)}",
                    car_number=f"BR-{random.randint(10,99)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                    area_hectares=round(random.uniform(50, 5000), 2),
                    city=random.choice(['Ribeirão Preto', 'Uberlândia', 'Dourados', 'Rio Verde', 'Sorriso']),
                    state=random.choice(['SP', 'MG', 'MS', 'GO', 'MT']),
                    owner_name=f"Proprietário {random.randint(1, 100)}",
                )
                db.add(property_data)
                total_properties += 1
        
        await db.commit()
        print(f"   ✅ {total_properties} propriedades criadas\n")
        
        # 4. Criar empresas
        print("🏢 Criando empresas...")
        total_companies = 0
        for investigation in investigations:
            num_companies = random.randint(1, 4)
            
            for i in range(num_companies):
                company = Company(
                    investigation_id=investigation.id,
                    name=f"{random.choice(['Agropecuária', 'Fazendas', 'Empreendimentos'])} {random.choice(['Vale Verde', 'Santa Helena', 'Boa Vista'])} Ltda",
                    cnpj=f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}/0001-{random.randint(10,99)}",
                    registration_date=datetime.utcnow() - timedelta(days=random.randint(365, 3650)),
                    status=random.choice(['ATIVA', 'ATIVA', 'ATIVA', 'SUSPENSA']),
                )
                db.add(company)
                total_companies += 1
        
        await db.commit()
        print(f"   ✅ {total_companies} empresas criadas\n")
        
        # 5. Criar contratos de arrendamento
        print("📝 Criando contratos...")
        total_contracts = 0
        result = await db.execute(select(Property))
        properties = result.scalars().all()
        
        for prop in random.sample(properties, min(len(properties), 20)):
            contract = LeaseContract(
                investigation_id=prop.investigation_id,
                property_id=prop.id,
                lessor_name=prop.owner_name,
                lessee_name=f"Arrendatário {random.randint(1, 50)}",
                start_date=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                end_date=datetime.utcnow() + timedelta(days=random.randint(365, 1825)),
                monthly_value=round(random.uniform(5000, 50000), 2),
                total_value=round(random.uniform(100000, 1000000), 2),
            )
            db.add(contract)
            total_contracts += 1
        
        await db.commit()
        print(f"   ✅ {total_contracts} contratos criados\n")
        
        # 6. Criar notificações
        print("🔔 Criando notificações...")
        total_notifications = 0
        
        notification_types = [
            (NotificationType.INVESTIGATION_CREATED, "Nova investigação criada", "A investigação foi criada com sucesso", NotificationPriority.LOW),
            (NotificationType.REPORT_READY, "📊 Relatório Pronto", "O relatório está pronto para download", NotificationPriority.HIGH),
            (NotificationType.INVESTIGATION_SHARED, "Investigação Compartilhada", "Uma investigação foi compartilhada com você", NotificationPriority.NORMAL),
            (NotificationType.ALERT, "⚠️ Alerta de Risco", "Score de risco elevado detectado", NotificationPriority.URGENT),
            (NotificationType.INVESTIGATION_UPDATED, "Dados Atualizados", "Novas informações encontradas", NotificationPriority.NORMAL),
        ]
        
        for user in users:
            user_investigations = [inv for inv in investigations if inv.user_id == user.id]
            
            for _ in range(random.randint(3, 8)):
                notif_type, title, message, priority = random.choice(notification_types)
                investigation = random.choice(user_investigations) if user_investigations else None
                
                notification = Notification(
                    user_id=user.id,
                    type=notif_type,
                    title=title,
                    message=message,
                    priority=priority,
                    investigation_id=investigation.id if investigation else None,
                    action_url=f'/investigations/{investigation.id}' if investigation else None,
                    is_read=random.choice([True, False, False]),
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
                )
                db.add(notification)
                total_notifications += 1
        
        await db.commit()
        print(f"   ✅ {total_notifications} notificações criadas\n")
        
        # 7. Criar comentários
        print("💬 Criando comentários...")
        total_comments = 0
        
        comments_templates = [
            "Encontrei informações importantes sobre esta propriedade.",
            "Verificar documentação no cartório local.",
            "CAR está irregular - necessário regularização.",
            "Confirmado com INCRA - área em processo de regularização.",
            "Proprietário possui outras áreas na região.",
            "NOTA INTERNA: Agendar reunião com cliente.",
        ]
        
        for investigation in random.sample(investigations, min(len(investigations), 15)):
            num_comments = random.randint(1, 4)
            
            for _ in range(num_comments):
                comment = InvestigationComment(
                    investigation_id=investigation.id,
                    user_id=investigation.user_id,
                    content=random.choice(comments_templates),
                    is_internal=random.choice([True, False]),
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 168)),
                )
                db.add(comment)
                total_comments += 1
        
        await db.commit()
        print(f"   ✅ {total_comments} comentários criados\n")
        
        print("=" * 70)
        print("  ✅ DADOS DE DEMONSTRAÇÃO CRIADOS COM SUCESSO!")
        print("=" * 70)
        print()
        print("📊 RESUMO:")
        print(f"   • {len(users)} usuários")
        print(f"   • {total_investigations} investigações")
        print(f"   • {total_properties} propriedades")
        print(f"   • {total_companies} empresas")
        print(f"   • {total_contracts} contratos")
        print(f"   • {total_notifications} notificações")
        print(f"   • {total_comments} comentários")
        print()
        print("🔐 CREDENCIAIS DE ACESSO:")
        print()
        for user_data in DEMO_USERS:
            print(f"   Email: {user_data['email']}")
            print(f"   Senha: {user_data['password']}")
            print()
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(create_demo_data())
