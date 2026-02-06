"""
Circuit Breaker Pattern para Serviços Externos
Protege a aplicação contra falhas em cascata
"""
import asyncio
import logging
import time
from enum import Enum
from typing import Optional, Dict, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    def __init__(self, service_name: str, reset_time: float):
        self.service_name = service_name
        self.reset_time = reset_time
        seconds_remaining = max(0, int(reset_time - time.monotonic()))
        super().__init__(
            f"Circuit breaker OPEN para '{service_name}'. "
            f"Próxima tentativa em {seconds_remaining}s."
        )


class CircuitBreaker:
    """
    Circuit Breaker individual para um serviço.
    
    States:
    - CLOSED: Normal operation. Counts failures.
    - OPEN: Too many failures. Rejects all requests immediately.
    - HALF_OPEN: After timeout, allows one test request.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 1,
        success_threshold: int = 2,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.success_threshold = success_threshold
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                self._success_count = 0
                logger.info(f"[circuit-breaker] '{self.name}' → HALF_OPEN")
        return self._state
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        async with self._lock:
            current_state = self.state
            
            if current_state == CircuitState.OPEN:
                raise CircuitBreakerError(self.name, self._last_failure_time + self.recovery_timeout)
            
            if current_state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerError(self.name, self._last_failure_time + self.recovery_timeout)
                self._half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as exc:
            await self._on_failure()
            raise
    
    async def _on_success(self):
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info(f"[circuit-breaker] '{self.name}' → CLOSED (recuperado)")
            else:
                self._failure_count = 0
    
    async def _on_failure(self):
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning(f"[circuit-breaker] '{self.name}' → OPEN (falha em half-open)")
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    f"[circuit-breaker] '{self.name}' → OPEN "
                    f"({self._failure_count} falhas consecutivas)"
                )
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }


class CircuitBreakerRegistry:
    """Registry global de circuit breakers."""
    
    _breakers: Dict[str, CircuitBreaker] = {}
    
    @classmethod
    def get_or_create(
        cls,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ) -> CircuitBreaker:
        if name not in cls._breakers:
            cls._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )
        return cls._breakers[name]
    
    @classmethod
    def get_all_status(cls) -> list:
        return [cb.get_status() for cb in cls._breakers.values()]
    
    @classmethod
    def reset(cls, name: str):
        if name in cls._breakers:
            cb = cls._breakers[name]
            cb._state = CircuitState.CLOSED
            cb._failure_count = 0
            cb._success_count = 0
            logger.info(f"[circuit-breaker] '{name}' resetado manualmente")


def circuit_protected(
    service_name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
):
    """Decorator que protege uma função com circuit breaker."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cb = CircuitBreakerRegistry.get_or_create(
                service_name, failure_threshold, recovery_timeout
            )
            return await cb.call(func, *args, **kwargs)
        return wrapper
    return decorator
