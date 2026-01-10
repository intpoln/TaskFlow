from datetime import timedelta

from celery import Celery

from src.config import settings

celery_instance = Celery("tasks", broker=settings.redis_url, include=["src.tasks.tasks"])

# celery_instance.conf.beat_schedule = {
#     "checkin_notify": {
#         "task": "check_celery",
#         "schedule": timedelta(seconds=5),
#     }
# }
