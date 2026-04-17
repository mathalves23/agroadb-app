"""
Sistema de Compliance LGPD (Lei Geral de Proteção de Dados)
Implementa funcionalidades para conformidade com a LGPD
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy import JSON
import logging

from app.core.database import Base

logger = logging.getLogger(__name__)


class ConsentType(str, Enum):
    """Tipos de consentimento LGPD"""
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    DATA_PROCESSING = "data_processing"
    MARKETING = "marketing"
    THIRD_PARTY_SHARING = "third_party_sharing"


class DataRetentionPolicy(str, Enum):
    """Políticas de retenção de dados"""
    INVESTIGATION_DATA = "investigation_data"  # 5 anos
    AUDIT_LOGS = "audit_logs"  # 2 anos
    USER_INACTIVE = "user_inactive"  # 1 ano de inatividade
    TEMPORARY_DATA = "temporary_data"  # 30 dias


class UserConsent(Base):
    """
    Modelo de Consentimento do Usuário
    
    Registra consentimentos dados pelos usuários conforme LGPD
    """
    __tablename__ = "user_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    consent_type = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)  # Versão do termo
    consented_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "consent_type": self.consent_type,
            "version": self.version,
            "consented_at": self.consented_at.isoformat() if self.consented_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "is_active": self.is_active
        }


class DataDeletionRequest(Base):
    """
    Modelo de Solicitação de Exclusão de Dados
    
    Registra solicitações de exclusão conforme direito do titular (Art. 18, VI da LGPD)
    """
    __tablename__ = "data_deletion_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    requested_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    reason = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed
    processed_at = Column(DateTime, nullable=True)
    processed_by = Column(Integer, nullable=True)  # ID do admin que processou
    notes = Column(Text, nullable=True)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "reason": self.reason,
            "status": self.status,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "processed_by": self.processed_by,
            "notes": self.notes
        }


class PersonalDataAccess(Base):
    """
    Modelo de Acesso a Dados Pessoais
    
    Registra acessos a dados pessoais para relatório LGPD
    """
    __tablename__ = "personal_data_accesses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    data_type = Column(String(100), nullable=False)  # cpf, cnpj, email, etc
    purpose = Column(String(200), nullable=False)  # Finalidade do acesso
    accessed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    accessed_by = Column(Integer, nullable=True)  # Quem acessou
    legal_basis = Column(String(100), nullable=True)  # Base legal (Art. 7 LGPD)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "data_type": self.data_type,
            "purpose": self.purpose,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "accessed_by": self.accessed_by,
            "legal_basis": self.legal_basis
        }


class LGPDService:
    """
    Serviço de Compliance LGPD
    
    Gerencia consentimentos, exclusão de dados e relatórios
    """
    
    # Versões atuais dos termos
    CURRENT_VERSIONS = {
        ConsentType.TERMS_OF_SERVICE: "1.0.0",
        ConsentType.PRIVACY_POLICY: "1.0.0",
        ConsentType.DATA_PROCESSING: "1.0.0",
    }
    
    # Retenção de dados (em dias)
    RETENTION_PERIODS = {
        DataRetentionPolicy.INVESTIGATION_DATA: 1825,  # 5 anos
        DataRetentionPolicy.AUDIT_LOGS: 730,  # 2 anos
        DataRetentionPolicy.USER_INACTIVE: 365,  # 1 ano
        DataRetentionPolicy.TEMPORARY_DATA: 30,  # 30 dias
    }
    
    @staticmethod
    async def record_consent(
        db,
        user_id: int,
        consent_type: ConsentType,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserConsent:
        """
        Registra consentimento do usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            consent_type: Tipo de consentimento
            ip_address: IP do usuário
            user_agent: User agent
            
        Returns:
            Registro de consentimento criado
        """
        version = LGPDService.CURRENT_VERSIONS.get(consent_type, "1.0.0")
        
        consent = UserConsent(
            user_id=user_id,
            consent_type=consent_type.value,
            version=version,
            consented_at=datetime.utcnow(),
            is_active=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(consent)
        await db.commit()
        await db.refresh(consent)
        
        logger.info(f"✅ Consentimento registrado: {consent_type.value} para usuário {user_id}")
        
        return consent
    
    @staticmethod
    async def revoke_consent(
        db,
        user_id: int,
        consent_type: ConsentType
    ) -> bool:
        """
        Revoga consentimento do usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            consent_type: Tipo de consentimento
            
        Returns:
            True se revogado com sucesso
        """
        from sqlalchemy import select, update
        
        query = update(UserConsent).where(
            UserConsent.user_id == user_id,
            UserConsent.consent_type == consent_type.value,
            UserConsent.is_active == True
        ).values(
            is_active=False,
            revoked_at=datetime.utcnow()
        )
        
        await db.execute(query)
        await db.commit()
        
        logger.info(f"🚫 Consentimento revogado: {consent_type.value} para usuário {user_id}")
        
        return True
    
    @staticmethod
    async def check_consent(
        db,
        user_id: int,
        consent_type: ConsentType
    ) -> bool:
        """
        Verifica se usuário tem consentimento ativo
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            consent_type: Tipo de consentimento
            
        Returns:
            True se tem consentimento ativo
        """
        from sqlalchemy import select
        
        query = select(UserConsent).where(
            UserConsent.user_id == user_id,
            UserConsent.consent_type == consent_type.value,
            UserConsent.is_active == True
        )
        
        result = await db.execute(query)
        consent = result.scalar_one_or_none()
        
        return consent is not None
    
    @staticmethod
    async def request_data_deletion(
        db,
        user_id: int,
        reason: Optional[str] = None
    ) -> DataDeletionRequest:
        """
        Cria solicitação de exclusão de dados (Direito à Exclusão - Art. 18, VI)
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            reason: Motivo da exclusão
            
        Returns:
            Solicitação criada
        """
        request = DataDeletionRequest(
            user_id=user_id,
            requested_at=datetime.utcnow(),
            reason=reason,
            status="pending"
        )
        
        db.add(request)
        await db.commit()
        await db.refresh(request)
        
        logger.info(f"📋 Solicitação de exclusão criada para usuário {user_id}")
        
        return request
    
    @staticmethod
    async def process_data_deletion(
        db,
        request_id: int,
        processed_by: int,
        notes: Optional[str] = None
    ) -> bool:
        """
        Processa solicitação de exclusão de dados
        
        Args:
            db: Sessão do banco
            request_id: ID da solicitação
            processed_by: ID do admin que processou
            notes: Notas sobre o processamento
            
        Returns:
            True se processado com sucesso
        """
        from sqlalchemy import select, update
        
        # Buscar solicitação
        query = select(DataDeletionRequest).where(DataDeletionRequest.id == request_id)
        result = await db.execute(query)
        request = result.scalar_one_or_none()
        
        if not request or request.status != "pending":
            return False
        
        # Marcar como processando
        request.status = "processing"
        await db.commit()
        
        try:
            # Aqui implementar lógica de exclusão real dos dados
            # Por exemplo:
            # - Anonimizar dados pessoais
            # - Excluir investigações (se permitido)
            # - Manter dados mínimos para obrigações legais
            
            # TODO: Implementar exclusão efetiva de dados
            # await delete_user_personal_data(db, request.user_id)
            
            # Marcar como concluído
            request.status = "completed"
            request.processed_at = datetime.utcnow()
            request.processed_by = processed_by
            request.notes = notes
            
            await db.commit()
            
            logger.info(f"✅ Solicitação de exclusão processada: {request_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar exclusão: {e}")
            request.status = "pending"
            await db.commit()
            return False
    
    @staticmethod
    async def record_personal_data_access(
        db,
        user_id: int,
        data_type: str,
        purpose: str,
        accessed_by: Optional[int] = None,
        legal_basis: Optional[str] = None
    ) -> PersonalDataAccess:
        """
        Registra acesso a dados pessoais (Art. 37 LGPD)
        
        Args:
            db: Sessão do banco
            user_id: ID do titular dos dados
            data_type: Tipo de dado acessado
            purpose: Finalidade do acesso
            accessed_by: Quem acessou
            legal_basis: Base legal do tratamento
            
        Returns:
            Registro de acesso
        """
        access = PersonalDataAccess(
            user_id=user_id,
            data_type=data_type,
            purpose=purpose,
            accessed_at=datetime.utcnow(),
            accessed_by=accessed_by,
            legal_basis=legal_basis or "Consentimento do titular"
        )
        
        db.add(access)
        await db.commit()
        
        return access
    
    @staticmethod
    async def generate_personal_data_report(
        db,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Gera relatório de dados pessoais processados (Direito de Acesso - Art. 18, II)
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            
        Returns:
            Relatório completo com todos os dados
        """
        from sqlalchemy import select, func
        
        # Buscar usuário
        from app.domain.user import User
        user_query = select(User).where(User.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            return {}
        
        # Consentimentos
        consent_query = select(UserConsent).where(UserConsent.user_id == user_id)
        consent_result = await db.execute(consent_query)
        consents = [c.to_dict() for c in consent_result.scalars().all()]
        
        # Acessos a dados pessoais (últimos 90 dias)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        access_query = select(PersonalDataAccess).where(
            PersonalDataAccess.user_id == user_id,
            PersonalDataAccess.accessed_at >= ninety_days_ago
        ).order_by(PersonalDataAccess.accessed_at.desc())
        access_result = await db.execute(access_query)
        accesses = [a.to_dict() for a in access_result.scalars().all()]
        
        # Estatísticas de acessos
        access_stats_query = select(
            PersonalDataAccess.data_type,
            func.count(PersonalDataAccess.id).label('count')
        ).where(
            PersonalDataAccess.user_id == user_id
        ).group_by(PersonalDataAccess.data_type)
        
        stats_result = await db.execute(access_stats_query)
        access_stats = {row.data_type: row.count for row in stats_result}
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "consents": consents,
            "personal_data_accesses": accesses,
            "access_statistics": access_stats,
            "data_retention_policies": {
                policy.value: days
                for policy, days in LGPDService.RETENTION_PERIODS.items()
            },
            "rights": {
                "confirmation": "Você tem direito de confirmar a existência de tratamento (Art. 18, I)",
                "access": "Você tem direito de acessar seus dados (Art. 18, II)",
                "correction": "Você tem direito de corrigir dados incompletos/incorretos (Art. 18, III)",
                "anonymization": "Você tem direito à anonimização, bloqueio ou eliminação (Art. 18, IV)",
                "portability": "Você tem direito à portabilidade dos dados (Art. 18, V)",
                "deletion": "Você tem direito de solicitar a eliminação (Art. 18, VI)",
                "information": "Você tem direito de saber com quem compartilhamos seus dados (Art. 18, VII)",
                "consent_revocation": "Você pode revogar o consentimento a qualquer momento (Art. 18, IX)"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def apply_retention_policy(
        db,
        policy: DataRetentionPolicy
    ) -> int:
        """
        Aplica política de retenção de dados
        
        Args:
            db: Sessão do banco
            policy: Política a aplicar
            
        Returns:
            Número de registros afetados
        """
        from sqlalchemy import delete
        
        retention_days = LGPDService.RETENTION_PERIODS.get(policy)
        if not retention_days:
            return 0
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        affected = 0
        
        if policy == DataRetentionPolicy.AUDIT_LOGS:
            from app.core.audit import AuditLog
            delete_query = delete(AuditLog).where(AuditLog.timestamp < cutoff_date)
            result = await db.execute(delete_query)
            affected = result.rowcount
        
        elif policy == DataRetentionPolicy.INVESTIGATION_DATA:
            # TODO: Implementar lógica para investigações antigas
            pass
        
        elif policy == DataRetentionPolicy.USER_INACTIVE:
            # TODO: Implementar lógica para usuários inativos
            pass
        
        elif policy == DataRetentionPolicy.TEMPORARY_DATA:
            # TODO: Implementar lógica para dados temporários
            pass
        
        await db.commit()
        
        logger.info(f"🗑️ Política de retenção aplicada: {policy.value} - {affected} registros afetados")
        
        return affected


# Instância global
lgpd_service = LGPDService()
