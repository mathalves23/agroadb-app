"""
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import engine, Base
from app.core.rate_limiting import RateLimitMiddleware
from app.core.circuit_breaker import CircuitBreakerRegistry
from app.core.indexes import create_optimized_indexes
from app.workers.scraper_workers import orchestrator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Lifecycle events for FastAPI application"""
    # Startup
    logger.info("🚀 Iniciando aplicação...")
    
    # Criar tabelas do banco
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Criar índices otimizados
    await create_optimized_indexes(engine)
    
    # Iniciar workers apenas quando habilitado
    if settings.ENABLE_WORKERS:
        asyncio.create_task(orchestrator.start_all_workers())
        logger.info("✅ Workers iniciados em background")
    else:
        logger.info("⚠️  Workers desabilitados (ENABLE_WORKERS=false)")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando aplicação...")
    if settings.ENVIRONMENT == "production":
        await orchestrator.stop_all_workers()
    await engine.dispose()
    logger.info("✅ Aplicação encerrada")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ============================================================================
# GLOBAL EXCEPTION HANDLER — garante que respostas de erro incluam CORS headers
# ============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Captura qualquer exceção não tratada e devolve JSON com status 500."""
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno: {str(exc)[:300]}"},
    )


# ============================================================================
# MIDDLEWARE — ORDEM IMPORTA (últimos adicionados executam primeiro)
# ============================================================================
# 1) Security Headers (executa por último, após CORS já ter sido aplicado)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        try:
            response = await call_next(request)
        except Exception:
            logger.error("SecurityHeaders middleware caught error: %s", traceback.format_exc())
            response = JSONResponse(status_code=500, content={"detail": "Erro interno do servidor"})
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.FORCE_HTTPS:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# 2) GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3) Rate Limiting
app.add_middleware(RateLimitMiddleware, redis_url=settings.REDIS_URL)

# 4) CORS — DEVE SER O ÚLTIMO add_middleware para que seja o PRIMEIRO a processar
# Em desenvolvimento: aceita localhost; em produção: usar CORS_ORIGINS do .env
_cors_origins = settings.CORS_ORIGINS if settings.ENVIRONMENT == "production" else [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=settings.CORS_MAX_AGE,
)

# 5) HTTPS Redirect (production only)
if settings.FORCE_HTTPS:
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)
    logger.info("🔒 HTTPS redirect habilitado")

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint"""
    return {
        "message": "AgroADB API",
        "version": settings.VERSION,
        "docs": "/api/docs",
    }


@app.get("/api/v1/circuit-breakers")
async def get_circuit_breaker_status():
    """Circuit breaker status for all registered services."""
    return CircuitBreakerRegistry.get_all_status()
