"""
Criptografia de Dados Sensíveis
Implementa criptografia para proteger dados pessoais e sensíveis
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """
    Serviço de Criptografia de Dados
    
    Usa Fernet (symmetric encryption) para criptografar dados sensíveis
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Inicializa o serviço de criptografia
        
        Args:
            encryption_key: Chave de criptografia (base64). Se None, usa variável de ambiente.
        """
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY")
        
        if not self.encryption_key:
            logger.warning(
                "⚠️ ENCRYPTION_KEY não configurada! Gerando chave temporária. "
                "Configure ENCRYPTION_KEY em produção!"
            )
            self.encryption_key = Fernet.generate_key().decode()
        
        self.fernet = Fernet(self.encryption_key.encode())
    
    @staticmethod
    def generate_key() -> str:
        """
        Gera uma nova chave de criptografia
        
        Returns:
            Chave em formato base64
        """
        key = Fernet.generate_key()
        return key.decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
        """
        Deriva uma chave de criptografia a partir de uma senha
        
        Args:
            password: Senha do usuário
            salt: Salt para derivação (se None, gera um novo)
            
        Returns:
            Tupla (chave_base64, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt
    
    def encrypt(self, data: str) -> str:
        """
        Criptografa dados
        
        Args:
            data: Dados em texto plano
            
        Returns:
            Dados criptografados em base64
        """
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"❌ Erro ao criptografar dados: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Descriptografa dados
        
        Args:
            encrypted_data: Dados criptografados em base64
            
        Returns:
            Dados descriptografados em texto plano
        """
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"❌ Erro ao descriptografar dados: {e}")
            raise
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list[str]) -> dict:
        """
        Criptografa campos específicos de um dicionário
        
        Args:
            data: Dicionário com dados
            fields_to_encrypt: Lista de campos a criptografar
            
        Returns:
            Dicionário com campos criptografados
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list[str]) -> dict:
        """
        Descriptografa campos específicos de um dicionário
        
        Args:
            data: Dicionário com dados criptografados
            fields_to_decrypt: Lista de campos a descriptografar
            
        Returns:
            Dicionário com campos descriptografados
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except Exception:
                    logger.warning(f"⚠️ Não foi possível descriptografar campo: {field}")
        
        return decrypted_data


# Campos sensíveis que devem ser criptografados
SENSITIVE_FIELDS = [
    "cpf",
    "cnpj",
    "rg",
    "passport",
    "phone",
    "email",  # Opcional dependendo do caso de uso
    "address",
    "bank_account",
    "credit_card",
    "ssn",
    "tax_id",
]


# Instância global
data_encryption = DataEncryption()


def encrypt_sensitive_data(data: dict) -> dict:
    """
    Helper para criptografar dados sensíveis em um dicionário
    
    Args:
        data: Dicionário com dados
        
    Returns:
        Dicionário com dados sensíveis criptografados
    """
    fields_to_encrypt = [field for field in SENSITIVE_FIELDS if field in data]
    return data_encryption.encrypt_dict(data, fields_to_encrypt)


def decrypt_sensitive_data(data: dict) -> dict:
    """
    Helper para descriptografar dados sensíveis em um dicionário
    
    Args:
        data: Dicionário com dados criptografados
        
    Returns:
        Dicionário com dados descriptografados
    """
    fields_to_decrypt = [field for field in SENSITIVE_FIELDS if field in data]
    return data_encryption.decrypt_dict(data, fields_to_decrypt)
