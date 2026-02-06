"""
Sistema de Webhooks para Integrações
Permite que sistemas externos recebam notificações de eventos
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import httpx
import hashlib
import hmac
import json
import logging
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy import JSON

from app.core.database import Base

logger = logging.getLogger(__name__)


class WebhookEvent(str, Enum):
    """Tipos de eventos de webhook"""
    INVESTIGATION_STARTED = "investigation.started"
    INVESTIGATION_COMPLETED = "investigation.completed"
    INVESTIGATION_FAILED = "investigation.failed"
    INVESTIGATION_CANCELLED = "investigation.cancelled"
    
    SCRAPER_COMPLETED = "scraper.completed"
    SCRAPER_FAILED = "scraper.failed"
    
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    
    DATA_DELETION_REQUESTED = "data.deletion_requested"


class Webhook(Base):
    """
    Modelo de Webhook
    
    Armazena configurações de webhooks por usuário
    """
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    url = Column(String(500), nullable=False)
    secret = Column(String(100), nullable=False)  # Para HMAC signature
    events = Column(JSON, nullable=False)  # Lista de eventos subscritos
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0, nullable=False)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "url": self.url,
            "events": self.events,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_triggered_at": self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            "failure_count": self.failure_count
        }


class WebhookDelivery(Base):
    """
    Log de entregas de webhook
    
    Rastreia todas as tentativas de entrega
    """
    __tablename__ = "webhook_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, nullable=False, index=True)
    event = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    delivered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    success = Column(Boolean, nullable=False)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "webhook_id": self.webhook_id,
            "event": self.event,
            "status_code": self.status_code,
            "success": self.success,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "error_message": self.error_message
        }


class WebhookService:
    """
    Serviço de Webhooks
    
    Gerencia envio de webhooks para integrações externas
    """
    
    MAX_FAILURES = 5  # Desabilita webhook após 5 falhas consecutivas
    TIMEOUT = 10  # Timeout de 10 segundos
    
    @staticmethod
    def generate_signature(payload: dict, secret: str) -> str:
        """
        Gera assinatura HMAC para webhook
        
        Args:
            payload: Dados do webhook
            secret: Secret do webhook
            
        Returns:
            Assinatura em formato sha256
        """
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @staticmethod
    async def trigger_webhook(
        db,
        webhook: Webhook,
        event: WebhookEvent,
        payload: Dict[str, Any]
    ) -> bool:
        """
        Dispara um webhook
        
        Args:
            db: Sessão do banco
            webhook: Configuração do webhook
            event: Tipo de evento
            payload: Dados do evento
            
        Returns:
            True se entregue com sucesso
        """
        # Verificar se webhook está ativo
        if not webhook.is_active:
            return False
        
        # Verificar se webhook está inscrito neste evento
        if event.value not in webhook.events:
            return False
        
        # Preparar payload
        webhook_payload = {
            "event": event.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        
        # Gerar assinatura
        signature = WebhookService.generate_signature(webhook_payload, webhook.secret)
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AgroADB-Webhook/1.0",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event.value,
            "X-Webhook-ID": str(webhook.id)
        }
        
        # Criar registro de entrega
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event=event.value,
            payload=webhook_payload,
            success=False
        )
        
        try:
            # Enviar webhook
            async with httpx.AsyncClient(timeout=WebhookService.TIMEOUT) as client:
                response = await client.post(
                    webhook.url,
                    json=webhook_payload,
                    headers=headers
                )
            
            # Registrar resposta
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:1000]  # Primeiros 1000 chars
            delivery.success = 200 <= response.status_code < 300
            
            if delivery.success:
                # Resetar contador de falhas
                webhook.failure_count = 0
                webhook.last_triggered_at = datetime.utcnow()
                
                logger.info(
                    f"✅ Webhook {webhook.id} entregue: {event.value} "
                    f"(status: {response.status_code})"
                )
            else:
                # Incrementar contador de falhas
                webhook.failure_count += 1
                delivery.error_message = f"HTTP {response.status_code}: {response.text[:200]}"
                
                logger.warning(
                    f"⚠️ Webhook {webhook.id} falhou: {event.value} "
                    f"(status: {response.status_code}, falhas: {webhook.failure_count})"
                )
                
                # Desabilitar se exceder máximo de falhas
                if webhook.failure_count >= WebhookService.MAX_FAILURES:
                    webhook.is_active = False
                    logger.error(
                        f"🚫 Webhook {webhook.id} desabilitado após {webhook.failure_count} falhas"
                    )
            
        except httpx.TimeoutException:
            delivery.error_message = "Timeout: Servidor não respondeu em 10s"
            delivery.success = False
            webhook.failure_count += 1
            
            logger.error(f"⏰ Webhook {webhook.id} timeout: {event.value}")
            
        except Exception as e:
            delivery.error_message = str(e)[:500]
            delivery.success = False
            webhook.failure_count += 1
            
            logger.error(f"❌ Erro ao enviar webhook {webhook.id}: {e}")
        
        # Salvar registro de entrega
        db.add(delivery)
        await db.commit()
        
        return delivery.success
    
    @staticmethod
    async def trigger_event(
        db,
        user_id: int,
        event: WebhookEvent,
        payload: Dict[str, Any]
    ):
        """
        Dispara evento para todos os webhooks do usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            event: Tipo de evento
            payload: Dados do evento
        """
        from sqlalchemy import select
        
        # Buscar webhooks ativos do usuário
        query = select(Webhook).where(
            Webhook.user_id == user_id,
            Webhook.is_active == True
        )
        result = await db.execute(query)
        webhooks = result.scalars().all()
        
        # Disparar cada webhook
        for webhook in webhooks:
            await WebhookService.trigger_webhook(db, webhook, event, payload)
    
    @staticmethod
    async def create_webhook(
        db,
        user_id: int,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Cria um novo webhook
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            url: URL do webhook
            events: Lista de eventos a subscrever
            secret: Secret para assinatura (gera automaticamente se None)
            
        Returns:
            Webhook criado
        """
        import secrets
        
        if secret is None:
            secret = secrets.token_urlsafe(32)
        
        webhook = Webhook(
            user_id=user_id,
            url=url,
            secret=secret,
            events=events,
            is_active=True,
            created_at=datetime.utcnow(),
            failure_count=0
        )
        
        db.add(webhook)
        await db.commit()
        await db.refresh(webhook)
        
        logger.info(f"✅ Webhook criado: {webhook.id} para user {user_id}")
        
        return webhook
    
    @staticmethod
    async def get_user_webhooks(db, user_id: int) -> List[Webhook]:
        """Retorna todos os webhooks de um usuário"""
        from sqlalchemy import select
        
        query = select(Webhook).where(Webhook.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_webhook_deliveries(
        db,
        webhook_id: int,
        limit: int = 50
    ) -> List[WebhookDelivery]:
        """Retorna histórico de entregas de um webhook"""
        from sqlalchemy import select, desc
        
        query = select(WebhookDelivery).where(
            WebhookDelivery.webhook_id == webhook_id
        ).order_by(
            desc(WebhookDelivery.delivered_at)
        ).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()


# Instância global
webhook_service = WebhookService()
