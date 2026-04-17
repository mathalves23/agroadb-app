"""
Índices otimizados para o banco de dados.
Executar na startup da aplicação para garantir performance.
"""
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

# SQL para criar índices otimizados
INDEXES = [
    # Investigations - filtros frequentes
    "CREATE INDEX IF NOT EXISTS ix_investigations_user_status ON investigations (user_id, status)",
    "CREATE INDEX IF NOT EXISTS ix_investigations_user_created ON investigations (user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS ix_investigations_cpf_cnpj ON investigations (target_cpf_cnpj) WHERE target_cpf_cnpj IS NOT NULL",
    "CREATE INDEX IF NOT EXISTS ix_investigations_status_priority ON investigations (status, priority DESC)",

    # Properties - consultas por investigação
    "CREATE INDEX IF NOT EXISTS ix_properties_investigation ON properties (investigation_id)",
    "CREATE INDEX IF NOT EXISTS ix_properties_car ON properties (car_number) WHERE car_number IS NOT NULL",
    "CREATE INDEX IF NOT EXISTS ix_properties_owner_cpf ON properties (owner_cpf_cnpj) WHERE owner_cpf_cnpj IS NOT NULL",

    # Companies - consultas por investigação
    "CREATE INDEX IF NOT EXISTS ix_companies_investigation ON companies (investigation_id)",
    "CREATE INDEX IF NOT EXISTS ix_companies_cnpj ON companies (cnpj)",

    # Legal queries - consultas por investigação e provedor
    "CREATE INDEX IF NOT EXISTS ix_legal_queries_investigation ON legal_queries (investigation_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS ix_legal_queries_provider ON legal_queries (provider, created_at DESC)",

    # Audit logs - consultas por usuário e recurso
    "CREATE INDEX IF NOT EXISTS ix_audit_logs_user ON audit_logs (user_id, timestamp DESC)",
    "CREATE INDEX IF NOT EXISTS ix_audit_logs_resource ON audit_logs (resource_type, resource_id)",
    "CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs (action, timestamp DESC)",

    # User consents - LGPD
    "CREATE INDEX IF NOT EXISTS ix_user_consents_user ON user_consents (user_id, consent_type)",

    # Collaboration
    "CREATE INDEX IF NOT EXISTS ix_investigation_shares_user ON investigation_shares (shared_with_id, is_active)",
    "CREATE INDEX IF NOT EXISTS ix_investigation_comments_inv ON investigation_comments (investigation_id, created_at DESC)",
]


async def create_optimized_indexes(engine: AsyncEngine):
    """Cria índices otimizados no banco de dados."""
    async with engine.begin() as conn:
        for idx_sql in INDEXES:
            try:
                await conn.execute(text(idx_sql))
            except Exception as e:
                # Some indexes may fail on SQLite (WHERE clause), ignore gracefully
                logger.debug(f"Índice ignorado (pode já existir ou não ser suportado): {e}")
    logger.info(f"✅ {len(INDEXES)} índices otimizados verificados/criados")
