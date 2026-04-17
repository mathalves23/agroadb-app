#!/usr/bin/env python3
"""
Cria um superutilizador na base de dados. Credenciais vêm apenas de variáveis de ambiente
(nada de passwords em ficheiros versionados).

Obrigatórias:
  AGROADB_ADMIN_EMAIL
  AGROADB_ADMIN_PASSWORD

Opcionais:
  AGROADB_ADMIN_USERNAME   (default: admin)
  AGROADB_ADMIN_FULL_NAME  (default: Administrator)

Exemplo (com Docker Compose, a partir da raiz do repositório):
  export AGROADB_ADMIN_EMAIL=admin@example.org
  export AGROADB_ADMIN_PASSWORD='use-uma-senha-forte'
  docker-compose exec -e AGROADB_ADMIN_EMAIL -e AGROADB_ADMIN_PASSWORD \\
    -e AGROADB_ADMIN_USERNAME -e AGROADB_ADMIN_FULL_NAME backend \\
    python scripts/create_superuser.py
"""
from __future__ import annotations

import asyncio
import os
import sys


def _require(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        print(f"Erro: defina a variável de ambiente {name}.", file=sys.stderr)
        sys.exit(1)
    return v


async def main() -> None:
    email = _require("AGROADB_ADMIN_EMAIL")
    password = _require("AGROADB_ADMIN_PASSWORD")
    username = os.environ.get("AGROADB_ADMIN_USERNAME", "admin").strip() or "admin"
    full_name = os.environ.get("AGROADB_ADMIN_FULL_NAME", "Administrator").strip() or "Administrator"

    from app.core.database import AsyncSessionLocal
    from app.core.security import get_password_hash
    from app.repositories.user import UserRepository

    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)
        if await repo.get_by_username(username):
            print(f"Já existe utilizador com username={username!r}. Nada a fazer.")
            return
        if await repo.get_by_email(email):
            print(f"Já existe utilizador com email={email!r}. Nada a fazer.")
            return

        await repo.create(
            {
                "email": email,
                "username": username,
                "full_name": full_name,
                "hashed_password": get_password_hash(password),
                "is_superuser": True,
                "is_active": True,
            }
        )
        await db.commit()
        print("Superutilizador criado. Guarde as credenciais com segurança e remova-as do histórico do terminal.")


if __name__ == "__main__":
    asyncio.run(main())
