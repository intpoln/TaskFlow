from src.integrations.email.client import email_client
from src.tasks.celery_app import celery_instance


@celery_instance.task(name="send_welcome_email")
def send_welcome_email(email: str):
    result = email_client.send_welcome(email)
    return result
