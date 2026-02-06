"""
Retry com Backoff Exponencial para Serviços Externos
"""
import asyncio
import logging
import random
from functools import wraps
from typing import Type, Tuple, Optional, Callable

import httpx

logger = logging.getLogger(__name__)

# Exceções que devem acionar retry
RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.RemoteProtocolError,
    ConnectionError,
    TimeoutError,
    OSError,
)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    retryable_status_codes: Tuple[int, ...] = (429, 500, 502, 503, 504),
    on_retry: Optional[Callable] = None,
):
    """
    Decorator para retry com backoff exponencial.
    
    Args:
        max_retries: Número máximo de tentativas (total = 1 + max_retries)
        base_delay: Delay base em segundos
        max_delay: Delay máximo em segundos
        exponential_base: Base da exponenciação
        jitter: Adicionar jitter aleatório para evitar thundering herd
        retryable_exceptions: Exceções que acionam retry
        retryable_status_codes: Status codes HTTP que acionam retry
        on_retry: Callback chamado antes de cada retry (attempt, exception, delay)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Check if result is an httpx.Response with retryable status
                    if isinstance(result, httpx.Response) and result.status_code in retryable_status_codes:
                        if attempt < max_retries:
                            delay = _calculate_delay(attempt, base_delay, max_delay, exponential_base, jitter)
                            logger.warning(
                                f"[retry] {func.__qualname__} retornou status {result.status_code}, "
                                f"tentativa {attempt + 1}/{max_retries + 1}, aguardando {delay:.1f}s"
                            )
                            if on_retry:
                                on_retry(attempt + 1, None, delay)
                            await asyncio.sleep(delay)
                            continue
                    
                    return result
                    
                except retryable_exceptions as exc:
                    last_exception = exc
                    
                    if attempt < max_retries:
                        delay = _calculate_delay(attempt, base_delay, max_delay, exponential_base, jitter)
                        logger.warning(
                            f"[retry] {func.__qualname__} falhou ({type(exc).__name__}), "
                            f"tentativa {attempt + 1}/{max_retries + 1}, aguardando {delay:.1f}s"
                        )
                        if on_retry:
                            on_retry(attempt + 1, exc, delay)
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"[retry] {func.__qualname__} falhou após {max_retries + 1} tentativas: {exc}"
                        )
                        raise
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def _calculate_delay(
    attempt: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool,
) -> float:
    """Calcula delay com backoff exponencial e jitter opcional."""
    delay = min(base_delay * (exponential_base ** attempt), max_delay)
    if jitter:
        delay = delay * (0.5 + random.random() * 0.5)
    return delay
