#!/bin/bash

# Script para criar um superusuário

echo "🔐 Criando superusuário..."

python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.core.security import get_password_hash

async def create_superuser():
    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        
        # Verificar se já existe
        existing = await user_repo.get_by_username('admin')
        if existing:
            print('⚠️  Superusuário admin já existe!')
            return
        
        # Criar superusuário
        user_data = {
            'email': 'admin@agroadb.com',
            'username': 'admin',
            'full_name': 'Administrator',
            'hashed_password': get_password_hash('admin123'),
            'is_superuser': True,
            'is_active': True,
        }
        
        await user_repo.create(user_data)
        await db.commit()
        
        print('✅ Superusuário criado com sucesso!')
        print('   Username: admin')
        print('   Password: admin123')
        print('   IMPORTANTE: Altere a senha após o primeiro login!')

asyncio.run(create_superuser())
"

echo "✅ Processo concluído!"
