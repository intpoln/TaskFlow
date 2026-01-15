"""Кастомные исключения приложения TaskFlow.

Модуль содержит иерархию исключений для обработки ошибок
на уровне бизнес-логики и репозиториев.
"""


class TaskFlowException(Exception):
    """Базовое исключение приложения TaskFlow.

    Все кастомные исключения наследуются от этого класса,
    что позволяет перехватывать любые ошибки приложения.

    Attributes:
        message: Текст сообщения об ошибке.
    """

    def __init__(self, message: str = "Неизвестная ошибка"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class NotFoundError(TaskFlowException):
    """Запрашиваемый ресурс не найден.

    Используется когда объект не существует в БД
    или недоступен текущему пользователю.
    """

    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(message)


class ForbiddenError(TaskFlowException):
    """Доступ к ресурсу запрещён.

    Используется когда пользователь аутентифицирован,
    но не имеет прав на выполнение операции.
    """

    def __init__(self, message: str = "Доступ запрещён"):
        super().__init__(message)


class ConflictError(TaskFlowException):
    """Конфликт при создании или обновлении ресурса.

    Используется при нарушении уникальности данных,
    например, дубликат email или username.
    """

    def __init__(self, message: str = "Ресурс уже существует"):
        super().__init__(message)


class NotAuthorizedError(TaskFlowException):
    """Требуется авторизация.

    Используется когда пользователь не аутентифицирован
    или токен доступа истёк/невалиден.
    """

    def __init__(self, message: str = "Требуется авторизация"):
        super().__init__(message)


class RepositoryError(TaskFlowException):
    """Ошибка на уровне репозитория.

    Используется для ошибок целостности данных:
    нарушение FK, CHECK constraint, NOT NULL и т.д.
    """

    def __init__(self, message: str = "Связанная запись не найдена"):
        super().__init__(message)
