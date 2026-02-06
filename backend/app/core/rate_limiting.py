"""
Rate Limiting Middleware
Implementa limitação de taxa de requisições para proteção da API
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import redis.asyncio as redis
import logging
import hashlib

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate Limiter usando Redis
    
    Implementa sliding window para contagem precisa de requisições
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        
        # Limites padrão (requisições por minuto)
        self.DEFAULT_LIMITS = {
            "anonymous": 20,  # 20 req/min para não autenticados
            "authenticated": 100,  # 100 req/min para autenticados
            "premium": 500,  # 500 req/min para usuários premium
        }
        
        # Limites específicos por endpoint (requisições por minuto)
        self.ENDPOINT_LIMITS = {
            "/api/v1/auth/login": 5,  # Login limitado (anti-brute force)
            "/api/v1/auth/register": 3,  # Registro limitado
            "/api/v1/auth/forgot-password": 3,  # Reset de senha limitado
            "/api/v1/investigations/": 50,  # Investigações moderado
        }
    
    async def connect(self):
        """Conecta ao Redis"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _get_identifier(self, request: Request) -> str:
        """
        Obtém identificador único para o cliente
        
        Prioridade: user_id > api_key > ip_address
        """
        # 1. Usuário autenticado
        user = getattr(request.state, "user", None)
        if user:
            return f"user:{user.id}"
        
        # 2. API Key (se implementado)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # Hash da API key para não expor
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            return f"api_key:{key_hash}"
        
        # 3. IP address (com fallback para X-Forwarded-For)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    def _get_limit(self, request: Request) -> int:
        """
        Determina o limite de rate para a requisição
        
        Returns:
            Número máximo de requisições por minuto
        """
        # Verificar limite específico do endpoint
        for endpoint, limit in self.ENDPOINT_LIMITS.items():
            if request.url.path.startswith(endpoint):
                return limit
        
        # Limite por tipo de usuário
        user = getattr(request.state, "user", None)
        if user:
            # Verificar se é premium (exemplo)
            if getattr(user, "is_premium", False):
                return self.DEFAULT_LIMITS["premium"]
            return self.DEFAULT_LIMITS["authenticated"]
        
        return self.DEFAULT_LIMITS["anonymous"]
    
    async def is_allowed(self, request: Request) -> Tuple[bool, Dict[str, any]]:
        """
        Verifica se a requisição é permitida
        
        Args:
            request: Requisição FastAPI
            
        Returns:
            Tupla (is_allowed, rate_limit_info)
        """
        if not self.redis_client:
            await self.connect()
        
        identifier = self._get_identifier(request)
        limit = self._get_limit(request)
        window = 60  # 1 minuto em segundos
        
        # Chave Redis: ratelimit:{identifier}:{timestamp}
        now = datetime.utcnow()
        current_window = int(now.timestamp() // window)
        key = f"ratelimit:{identifier}:{current_window}"
        
        try:
            # Incrementar contador
            current_count = await self.redis_client.incr(key)
            
            # Definir expiração na primeira requisição da janela
            if current_count == 1:
                await self.redis_client.expire(key, window * 2)  # 2 minutos para segurança
            
            # Calcular quando o limite reseta
            reset_time = (current_window + 1) * window
            remaining = max(0, limit - current_count)
            
            rate_limit_info = {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": reset_time - int(now.timestamp()) if current_count > limit else 0
            }
            
            is_allowed = current_count <= limit
            
            if not is_allowed:
                logger.warning(
                    f"🚫 Rate limit exceeded: {identifier} "
                    f"({current_count}/{limit} in {window}s window)"
                )
            
            return is_allowed, rate_limit_info
            
        except Exception as e:
            logger.error(f"❌ Erro no rate limiter: {e}")
            # Em caso de erro, permitir a requisição (fail-open)
            return True, {
                "limit": limit,
                "remaining": limit,
                "reset": int((now + timedelta(minutes=1)).timestamp())
            }
    
    async def check_and_raise(self, request: Request):
        """
        Verifica rate limit e levanta exceção se excedido
        
        Args:
            request: Requisição FastAPI
            
        Raises:
            HTTPException: Se rate limit excedido
        """
        is_allowed, info = await self.is_allowed(request)
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Try again in {info['retry_after']} seconds.",
                    "limit": info["limit"],
                    "retry_after": info["retry_after"]
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["retry_after"])
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de Rate Limiting
    
    Aplica rate limiting automaticamente a todas as requisições
    """
    
    def __init__(self, app: ASGIApp, redis_url: str = "redis://localhost:6379/0"):
        super().__init__(app)
        self.rate_limiter = RateLimiter(redis_url)
    
    async def dispatch(self, request: Request, call_next):
        """Processa requisição com rate limiting"""
        
        # Endpoints excluídos do rate limiting
        EXCLUDED_PATHS = [
            "/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/ws/",  # WebSockets
        ]
        
        # Verificar se path é excluído
        if any(request.url.path.startswith(path) for path in EXCLUDED_PATHS):
            return await call_next(request)
        
        # Verificar rate limit
        is_allowed, info = await self.rate_limiter.is_allowed(request)
        
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Try again in {info['retry_after']} seconds.",
                    "limit": info["limit"],
                    "retry_after": info["retry_after"]
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["retry_after"])
                }
            )
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response


# Instância global
rate_limiter = RateLimiter()
