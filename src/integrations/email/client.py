"""Клиент для отправки email через MailerSend."""

from mailersend import EmailBuilder, MailerSendClient

from src.config import settings


class EmailClient:
    def __init__(self):
        self._client = MailerSendClient(api_key=settings.MAILERSEND_API_KEY)
        self._from_email = settings.MAILERSEND_FROM_EMAIL
        self._from_name = settings.MAILSEND_FROM_NAME

    def send(self, to: str, subject: str, text: str) -> dict:
        builder = EmailBuilder().from_email(self._from_email).subject(subject).text(text).to(to)

        response = self._client.emails.send(builder.build())
        return {"status": response}

    def send_welcome(self, email: str) -> dict:
        return self.send(
            to=email,
            subject="Добро пожаловать в TaskFlow!",
            text="Вы успешно зарегистрировались на TaskFlow!",
        )


email_client = EmailClient()
