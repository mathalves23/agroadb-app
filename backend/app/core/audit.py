"""
Sistema de Audit Log Completo
Rastreia todas as ações dos usuários no sistema para compliance e segurança
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import json
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy import JSON
import logging

from app.core.database import Base

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Tipos de ações auditadas"""
    # Autenticação
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    PASSWORD_CHANGED = "auth.password_changed"
    PASSWORD_RESET = "auth.password_reset"
    TOKEN_REFRESHED = "auth.token_refreshed"
    
    # Usuários
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_VIEWED = "user.viewed"
    USER_LISTED = "user.listed"
    
    # Investigações
    INVESTIGATION_CREATED = "investigation.created"
    INVESTIGATION_UPDATED = "investigation.updated"
    INVESTIGATION_DELETED = "investigation.deleted"
    INVESTIGATION_VIEWED = "investigation.viewed"
    INVESTIGATION_LISTED = "investigation.listed"
    INVESTIGATION_STARTED = "investigation.started"
    INVESTIGATION_CANCELLED = "investigation.cancelled"
    
    # Dados Pessoais (LGPD)
    PERSONAL_DATA_ACCESSED = "lgpd.personal_data_accessed"
    PERSONAL_DATA_EXPORTED = "lgpd.personal_data_exported"
    PERSONAL_DATA_DELETED = "lgpd.personal_data_deleted"
    CONSENT_GIVEN = "lgpd.consent_given"
    CONSENT_REVOKED = "lgpd.consent_revoked"
    DATA_RETENTION_APPLIED = "lgpd.data_retention_applied"
    
    # Sistema
    API_KEY_CREATED = "system.api_key_created"
    API_KEY_REVOKED = "system.api_key_revoked"
    SETTINGS_CHANGED = "system.settings_changed"
    BACKUP_CREATED = "system.backup_created"
    
    # 2FA
    TWO_FA_ENABLED = "2fa.enabled"
    TWO_FA_DISABLED = "2fa.disabled"
    TWO_FA_VERIFIED = "2fa.verified"
    TWO_FA_FAILED = "2fa.failed"


class AuditLog(Base):
    """
    Modelo de Audit Log
    
    Armazena todas as ações realizadas no sistema para auditoria
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Quem?
    user_id = Column(Integer, nullable=True, index=True)  # None para ações sem auth
    username = Column(String(100), nullable=True)
    
    # O quê?
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True, index=True)  # user, investigation, etc
    resource_id = Column(String(100), nullable=True, index=True)
    
    # Quando?
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Onde?
    ip_address = Column(String(45), nullable=True)  # IPv6 suporta até 45 chars
    user_agent = Column(String(500), nullable=True)
    
    # Como?
    method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    endpoint = Column(String(500), nullable=True)
    
    # Detalhes
    details = Column(JSON, nullable=True)  # Dados adicionais em JSON
    
    # Resultado
    success = Column(String(10), nullable=False)  # success, failure, error
    error_message = Column(Text, nullable=True)
    
    # Índices compostos para queries comuns
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_action_timestamp', 'action', 'timestamp'),
        Index('idx_resource', 'resource_type', 'resource_id'),
    )
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "method": self.method,
            "endpoint": self.endpoint,
            "details": self.details,
            "success": self.success,
            "error_message": self.error_message
        }


class AuditLogger:
    """
    Serviço de Audit Logging
    
    Facilita o registro de ações de auditoria
    """
    
    @staticmethod
    async def log(
        db,
        action: AuditAction,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Registra uma ação de auditoria
        
        Args:
            db: Sessão do banco de dados
            action: Tipo de ação
            user_id: ID do usuário
            username: Nome do usuário
            resource_type: Tipo de recurso afetado
            resource_id: ID do recurso afetado
            ip_address: IP do usuário
            user_agent: User agent do navegador
            method: Método HTTP
            endpoint: Endpoint da API
            details: Detalhes adicionais em JSON
            success: Se a ação foi bem-sucedida
            error_message: Mensagem de erro (se houver)
            
        Returns:
            AuditLog criado
        """
        try:
            # Remover dados sensíveis dos detalhes
            safe_details = AuditLogger._sanitize_details(details) if details else None
            
            audit_log = AuditLog(
                user_id=user_id,
                username=username,
                action=action.value,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                method=method,
                endpoint=endpoint,
                details=safe_details,
                success="success" if success else "failure",
                error_message=error_message
            )
            
            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)
            
            logger.info(
                f"Audit log: {action.value} by user {user_id} ({username}) - {resource_type}:{resource_id}"
            )
            
            return audit_log
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar audit log: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def log_action(
        db,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """Compat: registra ação com string livre."""
        try:
            safe_details = AuditLogger._sanitize_details(details) if details else None
            audit_log = AuditLog(
                user_id=user_id,
                username=None,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                method=method,
                endpoint=endpoint,
                details=safe_details,
                success="success" if success else "failure",
                error_message=error_message,
            )
            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)
            return audit_log
        except Exception as e:
            logger.error(f"❌ Erro ao criar audit log: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    def _sanitize_details(details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove dados sensíveis dos detalhes
        
        Args:
            details: Detalhes originais
            
        Returns:
            Detalhes sanitizados
        """
        sensitive_keys = [
            'password', 'token', 'secret', 'api_key', 'private_key',
            'credit_card', 'ssn', 'cpf', 'cnpj'
        ]
        
        sanitized = {}
        for key, value in details.items():
            # Verificar se é chave sensível
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = AuditLogger._sanitize_details(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    async def get_user_logs(
        db,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Retorna logs de um usuário específico
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            limit: Limite de resultados
            offset: Offset para paginação
            
        Returns:
            Lista de logs
        """
        from sqlalchemy import select, desc
        
        query = select(AuditLog).where(
            AuditLog.user_id == user_id
        ).order_by(
            desc(AuditLog.timestamp)
        ).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_resource_logs(
        db,
        resource_type: str,
        resource_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Retorna logs de um recurso específico
        
        Args:
            db: Sessão do banco
            resource_type: Tipo de recurso
            resource_id: ID do recurso
            limit: Limite de resultados
            
        Returns:
            Lista de logs
        """
        from sqlalchemy import select, desc
        
        query = select(AuditLog).where(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == str(resource_id)
        ).order_by(
            desc(AuditLog.timestamp)
        ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def search_logs(
        db,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        success_only: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[AuditLog], int]:
        """
        Busca logs com filtros
        
        Args:
            db: Sessão do banco
            user_id: Filtrar por usuário
            action: Filtrar por ação
            resource_type: Filtrar por tipo de recurso
            start_date: Data inicial
            end_date: Data final
            ip_address: Filtrar por IP
            success_only: Apenas sucessos
            limit: Limite de resultados
            offset: Offset para paginação
            
        Returns:
            Tupla (logs, total_count)
        """
        from sqlalchemy import select, desc, func
        
        # Query base
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))
        
        # Aplicar filtros
        filters = []
        
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        
        if action:
            filters.append(AuditLog.action == action)
        
        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)
        
        if start_date:
            filters.append(AuditLog.timestamp >= start_date)
        
        if end_date:
            filters.append(AuditLog.timestamp <= end_date)
        
        if ip_address:
            filters.append(AuditLog.ip_address == ip_address)
        
        if success_only is not None:
            status = "success" if success_only else "failure"
            filters.append(AuditLog.success == status)
        
        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)
        
        # Ordenar e paginar
        query = query.order_by(desc(AuditLog.timestamp)).limit(limit).offset(offset)
        
        # Executar queries
        result = await db.execute(query)
        logs = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        return logs, total_count
    
    @staticmethod
    async def get_statistics(
        db,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Retorna estatísticas de auditoria
        
        Args:
            db: Sessão do banco
            user_id: Filtrar por usuário
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dicionário com estatísticas
        """
        from sqlalchemy import select, func
        
        # Filtros base
        filters = []
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if start_date:
            filters.append(AuditLog.timestamp >= start_date)
        if end_date:
            filters.append(AuditLog.timestamp <= end_date)
        
        # Total de logs
        total_query = select(func.count(AuditLog.id))
        if filters:
            total_query = total_query.where(*filters)
        
        total_result = await db.execute(total_query)
        total = total_result.scalar()
        
        # Ações mais comuns
        actions_query = select(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc()).limit(10)
        
        if filters:
            actions_query = actions_query.where(*filters)
        
        actions_result = await db.execute(actions_query)
        top_actions = [
            {"action": row.action, "count": row.count}
            for row in actions_result
        ]
        
        # Taxa de sucesso
        success_query = select(
            AuditLog.success,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.success)
        
        if filters:
            success_query = success_query.where(*filters)
        
        success_result = await db.execute(success_query)
        success_rates = {row.success: row.count for row in success_result}
        
        return {
            "total_logs": total,
            "top_actions": top_actions,
            "success_rate": {
                "success": success_rates.get("success", 0),
                "failure": success_rates.get("failure", 0),
                "percentage": (
                    success_rates.get("success", 0) / total * 100
                    if total > 0 else 0
                )
            }
        }


# Singleton para uso fácil
audit_logger = AuditLogger()
