import asyncio
import logging

from src.tasks.celery_app import celery_instance


async def log_celery_beat():
    logging.info("celery beat")

@celery_instance.task(name="check_celery")
def notify_users_with_today_checkin():
    asyncio.run(log_celery_beat())