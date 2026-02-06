"""
Autenticação de Dois Fatores (2FA)
Implementa TOTP (Time-based One-Time Password) para segurança adicional
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import logging

from app.core.database import Base

logger = logging.getLogger(__name__)


class TwoFactorAuth(Base):
    """
    Modelo de 2FA
    
    Armazena configurações de autenticação de dois fatores por usuário
    """
    __tablename__ = "two_factor_auth"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    secret = Column(String(32), nullable=False)  # Secret TOTP
    is_enabled = Column(Boolean, default=False, nullable=False)
    backup_codes = Column(String(500), nullable=True)  # Códigos de backup separados por vírgula
    
    # Relacionamento
    # user = relationship("User", back_populates="two_factor")
    
    def to_dict(self) -> dict:
        """Converte para dicionário (sem expor secret)"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_enabled": self.is_enabled,
            "has_backup_codes": bool(self.backup_codes)
        }


class TwoFactorService:
    """
    Serviço de Autenticação de Dois Fatores
    
    Implementa TOTP (compatível com Google Authenticator, Authy, etc)
    """
    
    @staticmethod
    def generate_secret() -> str:
        """
        Gera um novo secret TOTP
        
        Returns:
            Secret em base32
        """
        return pyotp.random_base32()
    
    @staticmethod
    def generate_backup_codes(count: int = 8) -> list[str]:
        """
        Gera códigos de backup
        
        Args:
            count: Número de códigos a gerar
            
        Returns:
            Lista de códigos de backup
        """
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            # Gerar código de 8 caracteres
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Formatar como XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        
        return codes
    
    @staticmethod
    def get_totp_uri(secret: str, user_email: str, issuer: str = "AgroADB") -> str:
        """
        Gera URI TOTP para QR Code
        
        Args:
            secret: Secret TOTP
            user_email: Email do usuário
            issuer: Nome da aplicação
            
        Returns:
            URI TOTP
        """
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )
    
    @staticmethod
    def generate_qr_code(secret: str, user_email: str) -> str:
        """
        Gera QR Code para configuração do 2FA
        
        Args:
            secret: Secret TOTP
            user_email: Email do usuário
            
        Returns:
            QR Code em base64
        """
        uri = TwoFactorService.get_totp_uri(secret, user_email)
        
        # Gerar QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Verifica token TOTP
        
        Args:
            secret: Secret TOTP
            token: Token fornecido pelo usuário (6 dígitos)
            
        Returns:
            True se token válido, False caso contrário
        """
        try:
            totp = pyotp.TOTP(secret)
            # valid_window=1 aceita tokens de até 30s antes/depois (tolerância de clock)
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.error(f"❌ Erro ao verificar token 2FA: {e}")
            return False
    
    @staticmethod
    def verify_backup_code(stored_codes: str, provided_code: str) -> tuple[bool, Optional[str]]:
        """
        Verifica código de backup
        
        Args:
            stored_codes: Códigos armazenados (separados por vírgula)
            provided_code: Código fornecido pelo usuário
            
        Returns:
            Tupla (is_valid, remaining_codes)
        """
        if not stored_codes:
            return False, None
        
        codes = [c.strip() for c in stored_codes.split(",")]
        provided_clean = provided_code.strip().upper()
        
        if provided_clean in codes:
            # Remover código usado
            codes.remove(provided_clean)
            remaining = ",".join(codes) if codes else None
            return True, remaining
        
        return False, stored_codes
    
    @staticmethod
    async def enable_2fa(db, user_id: int, user_email: str) -> dict:
        """
        Habilita 2FA para um usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            user_email: Email do usuário
            
        Returns:
            Dicionário com secret, QR code e códigos de backup
        """
        from sqlalchemy import select
        
        # Verificar se já existe
        query = select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        result = await db.execute(query)
        two_fa = result.scalar_one_or_none()
        
        # Gerar novo secret
        secret = TwoFactorService.generate_secret()
        backup_codes = TwoFactorService.generate_backup_codes()
        
        if two_fa:
            # Atualizar existente
            two_fa.secret = secret
            two_fa.is_enabled = False  # Precisa confirmar primeiro
            two_fa.backup_codes = ",".join(backup_codes)
        else:
            # Criar novo
            two_fa = TwoFactorAuth(
                user_id=user_id,
                secret=secret,
                is_enabled=False,
                backup_codes=",".join(backup_codes)
            )
            db.add(two_fa)
        
        await db.commit()
        
        # Gerar QR Code
        qr_code = TwoFactorService.generate_qr_code(secret, user_email)
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "message": "Scan the QR code with your authenticator app and verify to enable 2FA"
        }
    
    @staticmethod
    async def confirm_and_enable_2fa(db, user_id: int, token: str) -> bool:
        """
        Confirma e ativa 2FA
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            token: Token fornecido pelo usuário
            
        Returns:
            True se ativado com sucesso, False caso contrário
        """
        from sqlalchemy import select
        
        query = select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        result = await db.execute(query)
        two_fa = result.scalar_one_or_none()
        
        if not two_fa:
            return False
        
        # Verificar token
        if TwoFactorService.verify_token(two_fa.secret, token):
            two_fa.is_enabled = True
            await db.commit()
            logger.info(f"✅ 2FA habilitado para usuário {user_id}")
            return True
        
        logger.warning(f"⚠️ Token 2FA inválido para usuário {user_id}")
        return False
    
    @staticmethod
    async def disable_2fa(db, user_id: int, token: str) -> bool:
        """
        Desabilita 2FA
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            token: Token de confirmação
            
        Returns:
            True se desabilitado com sucesso
        """
        from sqlalchemy import select
        
        query = select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        result = await db.execute(query)
        two_fa = result.scalar_one_or_none()
        
        if not two_fa or not two_fa.is_enabled:
            return False
        
        # Verificar token antes de desabilitar
        if TwoFactorService.verify_token(two_fa.secret, token):
            two_fa.is_enabled = False
            await db.commit()
            logger.info(f"✅ 2FA desabilitado para usuário {user_id}")
            return True
        
        return False
    
    @staticmethod
    async def verify_2fa(db, user_id: int, token: str) -> bool:
        """
        Verifica token 2FA durante login
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            token: Token fornecido
            
        Returns:
            True se válido
        """
        from sqlalchemy import select
        
        query = select(TwoFactorAuth).where(
            TwoFactorAuth.user_id == user_id,
            TwoFactorAuth.is_enabled == True
        )
        result = await db.execute(query)
        two_fa = result.scalar_one_or_none()
        
        if not two_fa:
            return True  # 2FA não habilitado
        
        # Tentar verificar como token TOTP
        if TwoFactorService.verify_token(two_fa.secret, token):
            return True
        
        # Tentar verificar como código de backup
        is_valid, remaining_codes = TwoFactorService.verify_backup_code(
            two_fa.backup_codes,
            token
        )
        
        if is_valid:
            # Atualizar códigos de backup
            two_fa.backup_codes = remaining_codes
            await db.commit()
            logger.warning(f"⚠️ Código de backup usado para usuário {user_id}")
            return True
        
        return False
    
    @staticmethod
    async def get_status(db, user_id: int) -> Optional[dict]:
        """
        Retorna status do 2FA para um usuário
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            
        Returns:
            Dicionário com status ou None
        """
        from sqlalchemy import select
        
        query = select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        result = await db.execute(query)
        two_fa = result.scalar_one_or_none()
        
        if two_fa:
            return two_fa.to_dict()
        
        return None


# Instância global
two_factor_service = TwoFactorService()
