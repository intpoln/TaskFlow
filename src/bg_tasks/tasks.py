import asyncio

from src.bg_tasks.celery_app import celery_instance


async def log_celery_beat():
    pass


@celery_instance.task(name="check_celery")
def notify_users_with_today_checkin():
    asyncio.run(log_celery_beat())
