"""
Sistema de Cache Redis - Otimização de Performance
Implementa cache para queries frequentes e reduz carga no banco
"""
from typing import Optional, Any, Callable
from datetime import timedelta
import json
import logging
from functools import wraps
import hashlib
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheService:
    """
    Serviço de Cache Redis
    
    Implementa estratégias de cache para otimização de performance
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = 300  # 5 minutos
        
        # TTLs específicos por tipo de dado
        self.ttls = {
            'user': 600,  # 10 minutos
            'investigation': 300,  # 5 minutos
            'scraper_result': 1800,  # 30 minutos
            'statistics': 3600,  # 1 hora
            'public_data': 7200,  # 2 horas
            'search': 600,  # 10 minutos
        }
    
    async def connect(self):
        """Conecta ao Redis"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("✅ Cache Redis conectado")
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("🔌 Cache Redis desconectado")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Gera chave única para cache
        
        Args:
            prefix: Prefixo da chave
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Chave única para o cache
        """
        # Criar string única com todos os parâmetros
        params = f"{args}:{sorted(kwargs.items())}"
        hash_params = hashlib.md5(params.encode()).hexdigest()[:12]
        return f"cache:{prefix}:{hash_params}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Recupera valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor ou None se não encontrado
        """
        try:
            if not self.redis_client:
                await self.connect()
            
            value = await self.redis_client.get(key)
            
            if value:
                logger.debug(f"🎯 Cache HIT: {key}")
                return json.loads(value)
            
            logger.debug(f"❌ Cache MISS: {key}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar do cache: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Armazena valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: Time to live em segundos
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            if not self.redis_client:
                await self.connect()
            
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            
            await self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao armazenar no cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Remove valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            True se removido com sucesso
        """
        try:
            if not self.redis_client:
                await self.connect()
            
            await self.redis_client.delete(key)
            logger.debug(f"🗑️ Cache DELETE: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover do cache: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Remove todas as chaves que correspondem ao padrão
        
        Args:
            pattern: Padrão para buscar chaves (ex: "cache:user:*")
            
        Returns:
            Número de chaves removidas
        """
        try:
            if not self.redis_client:
                await self.connect()
            
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"🗑️ Cache DELETE PATTERN: {pattern} ({deleted} chaves)")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover padrão do cache: {e}")
            return 0
    
    async def get_stats(self) -> dict:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            if not self.redis_client:
                await self.connect()
            
            info = await self.redis_client.info('stats')
            
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                ),
                'keys_count': await self.redis_client.dbsize(),
                'memory_used': info.get('used_memory_human', 'N/A')
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calcula taxa de acerto do cache"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    # Métodos específicos para diferentes tipos de dados
    
    async def get_investigation(self, investigation_id: str) -> Optional[dict]:
        """Recupera investigação do cache"""
        key = f"cache:investigation:{investigation_id}"
        return await self.get(key)
    
    async def set_investigation(self, investigation_id: str, data: dict) -> bool:
        """Armazena investigação no cache"""
        key = f"cache:investigation:{investigation_id}"
        return await self.set(key, data, ttl=self.ttls['investigation'])
    
    async def invalidate_investigation(self, investigation_id: str):
        """Invalida cache de investigação"""
        await self.delete_pattern(f"cache:investigation:{investigation_id}*")
        await self.delete_pattern(f"cache:search:*{investigation_id}*")
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Recupera usuário do cache"""
        key = f"cache:user:{user_id}"
        return await self.get(key)
    
    async def set_user(self, user_id: int, data: dict) -> bool:
        """Armazena usuário no cache"""
        key = f"cache:user:{user_id}"
        return await self.set(key, data, ttl=self.ttls['user'])
    
    async def invalidate_user(self, user_id: int):
        """Invalida cache de usuário"""
        await self.delete_pattern(f"cache:user:{user_id}*")
    
    async def get_statistics(self, stat_type: str, **filters) -> Optional[dict]:
        """Recupera estatísticas do cache"""
        key = self._generate_key(f"statistics:{stat_type}", **filters)
        return await self.get(key)
    
    async def set_statistics(self, stat_type: str, data: dict, **filters) -> bool:
        """Armazena estatísticas no cache"""
        key = self._generate_key(f"statistics:{stat_type}", **filters)
        return await self.set(key, data, ttl=self.ttls['statistics'])


# Instância global
cache_service = CacheService()


# Decorator para cache automático
def cached(
    prefix: str,
    ttl: Optional[int] = None,
    key_func: Optional[Callable] = None
):
    """
    Decorator para cachear resultado de funções
    
    Args:
        prefix: Prefixo da chave de cache
        ttl: Time to live em segundos
        key_func: Função customizada para gerar chave
        
    Usage:
        @cached(prefix="user_profile", ttl=600)
        async def get_user_profile(user_id: int):
            return await db.query(...)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_service._generate_key(prefix, *args, **kwargs)
            
            # Tentar recuperar do cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Armazenar no cache
            if result is not None:
                await cache_service.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# Exemplo de uso
"""
# Em um endpoint:
@router.get("/users/{user_id}")
@cached(prefix="user", ttl=600)
async def get_user(user_id: int, db = Depends(get_db)):
    user = await db.query(User).filter(User.id == user_id).first()
    return user.to_dict()

# Ou manualmente:
async def get_investigation(investigation_id: str):
    # Tentar cache primeiro
    cached = await cache_service.get_investigation(investigation_id)
    if cached:
        return cached
    
    # Buscar do banco
    investigation = await db.query(...)
    
    # Armazenar no cache
    await cache_service.set_investigation(investigation_id, investigation)
    
    return investigation
"""
