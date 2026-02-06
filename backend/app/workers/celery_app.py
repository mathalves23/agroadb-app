"""
Celery Application Configuration
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "agroadb_workers",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers"])
