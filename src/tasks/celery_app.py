from celery import Celery

from src.config import settings

celery_instance = Celery(
    "celery_tasks", broker=settings.RABBIT_URI, include=["src.tasks.email_tasks"]
)
