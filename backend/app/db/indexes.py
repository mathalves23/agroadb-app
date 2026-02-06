"""
Índices Otimizados do Banco de Dados
Define índices para melhorar performance de queries
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Index


def create_optimized_indexes():
    """
    Cria índices otimizados para melhor performance
    
    Execute via migration Alembic:
    alembic revision --autogenerate -m "add_optimized_indexes"
    """
    
    # ========== USERS ==========
    # Busca por email (login)
    op.create_index(
        'idx_users_email',
        'users',
        ['email'],
        unique=True
    )
    
    # Busca por status ativo
    op.create_index(
        'idx_users_is_active',
        'users',
        ['is_active']
    )
    
    # ========== INVESTIGATIONS ==========
    # Busca por usuário (minhas investigações)
    op.create_index(
        'idx_investigations_user_id',
        'investigations',
        ['user_id']
    )
    
    # Busca por status
    op.create_index(
        'idx_investigations_status',
        'investigations',
        ['status']
    )
    
    # Ordenação por data de criação (timeline)
    op.create_index(
        'idx_investigations_created_at',
        'investigations',
        ['created_at'],
        postgresql_using='btree'
    )
    
    # Busca combinada: usuário + status + data (query comum)
    op.create_index(
        'idx_investigations_user_status_created',
        'investigations',
        ['user_id', 'status', 'created_at']
    )
    
    # Full-text search no nome do alvo
    op.execute("""
        CREATE INDEX idx_investigations_target_name_fts 
        ON investigations 
        USING gin(to_tsvector('portuguese', target_name))
    """)
    
    # Busca por CPF/CNPJ
    op.create_index(
        'idx_investigations_target_cpf_cnpj',
        'investigations',
        ['target_cpf_cnpj']
    )
    
    # ========== AUDIT LOGS ==========
    # Busca por usuário
    op.create_index(
        'idx_audit_logs_user_id',
        'audit_logs',
        ['user_id']
    )
    
    # Busca por ação
    op.create_index(
        'idx_audit_logs_action',
        'audit_logs',
        ['action']
    )
    
    # Busca por recurso
    op.create_index(
        'idx_audit_logs_resource',
        'audit_logs',
        ['resource_type', 'resource_id']
    )
    
    # Ordenação por timestamp
    op.create_index(
        'idx_audit_logs_timestamp',
        'audit_logs',
        ['timestamp'],
        postgresql_using='btree'
    )
    
    # Busca combinada: usuário + data (relatórios de auditoria)
    op.create_index(
        'idx_audit_logs_user_timestamp',
        'audit_logs',
        ['user_id', 'timestamp']
    )
    
    # ========== NOTIFICATIONS ==========
    # Busca por usuário + lida
    op.create_index(
        'idx_notifications_user_read',
        'in_app_notifications',
        ['user_id', 'read']
    )
    
    # Ordenação por data
    op.create_index(
        'idx_notifications_created_at',
        'in_app_notifications',
        ['created_at'],
        postgresql_using='btree'
    )
    
    # Busca por categoria
    op.create_index(
        'idx_notifications_category',
        'in_app_notifications',
        ['category']
    )
    
    # ========== WEBHOOKS ==========
    # Busca por usuário + ativo
    op.create_index(
        'idx_webhooks_user_active',
        'webhooks',
        ['user_id', 'is_active']
    )
    
    # ========== WEBHOOK DELIVERIES ==========
    # Busca por webhook + data
    op.create_index(
        'idx_webhook_deliveries_webhook_delivered',
        'webhook_deliveries',
        ['webhook_id', 'delivered_at']
    )
    
    # Busca por sucesso (monitoramento)
    op.create_index(
        'idx_webhook_deliveries_success',
        'webhook_deliveries',
        ['success']
    )
    
    # ========== TWO FACTOR AUTH ==========
    # Busca por usuário
    op.create_index(
        'idx_two_factor_user_id',
        'two_factor_auth',
        ['user_id'],
        unique=True
    )
    
    # ========== LGPD CONSENT ==========
    # Busca por usuário + tipo
    op.create_index(
        'idx_user_consent_user_type',
        'user_consents',
        ['user_id', 'consent_type']
    )
    
    # Busca por ativo
    op.create_index(
        'idx_user_consent_is_active',
        'user_consents',
        ['is_active']
    )
    
    # ========== DATA DELETION REQUESTS ==========
    # Busca por usuário + status
    op.create_index(
        'idx_deletion_requests_user_status',
        'data_deletion_requests',
        ['user_id', 'status']
    )
    
    # Busca por data de requisição
    op.create_index(
        'idx_deletion_requests_requested_at',
        'data_deletion_requests',
        ['requested_at']
    )
    
    # ========== PERSONAL DATA ACCESS ==========
    # Busca por usuário + data
    op.create_index(
        'idx_personal_data_access_user_accessed',
        'personal_data_accesses',
        ['user_id', 'accessed_at']
    )
    
    print("✅ Índices otimizados criados com sucesso!")


def drop_optimized_indexes():
    """Remove índices (para rollback)"""
    indexes = [
        'idx_users_email',
        'idx_users_is_active',
        'idx_investigations_user_id',
        'idx_investigations_status',
        'idx_investigations_created_at',
        'idx_investigations_user_status_created',
        'idx_investigations_target_name_fts',
        'idx_investigations_target_cpf_cnpj',
        'idx_audit_logs_user_id',
        'idx_audit_logs_action',
        'idx_audit_logs_resource',
        'idx_audit_logs_timestamp',
        'idx_audit_logs_user_timestamp',
        'idx_notifications_user_read',
        'idx_notifications_created_at',
        'idx_notifications_category',
        'idx_webhooks_user_active',
        'idx_webhook_deliveries_webhook_delivered',
        'idx_webhook_deliveries_success',
        'idx_two_factor_user_id',
        'idx_user_consent_user_type',
        'idx_user_consent_is_active',
        'idx_deletion_requests_user_status',
        'idx_deletion_requests_requested_at',
        'idx_personal_data_access_user_accessed'
    ]
    
    for index in indexes:
        try:
            op.drop_index(index)
        except:
            pass


# Estatísticas de uso dos índices
INDEX_USAGE_QUERY = """
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM
    pg_stat_user_indexes
WHERE
    schemaname = 'public'
ORDER BY
    idx_scan DESC;
"""

# Query para encontrar índices não utilizados
UNUSED_INDEXES_QUERY = """
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM
    pg_stat_user_indexes
WHERE
    schemaname = 'public'
    AND idx_scan = 0
    AND indexname NOT LIKE '%_pkey'
ORDER BY
    tablename, indexname;
"""

# Queries lentas (identificar necessidade de novos índices)
SLOW_QUERIES_QUERY = """
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM
    pg_stat_statements
WHERE
    query NOT LIKE '%pg_stat%'
ORDER BY
    mean_time DESC
LIMIT 20;
"""


# Exemplo de uso em migration Alembic
"""
# alembic/versions/xxx_add_optimized_indexes.py

from alembic import op
import sqlalchemy as sa
from app.db.indexes import create_optimized_indexes, drop_optimized_indexes

def upgrade():
    create_optimized_indexes()

def downgrade():
    drop_optimized_indexes()
"""
