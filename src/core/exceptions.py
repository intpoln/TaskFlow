class TaskFlowException(Exception):
    def __init__(self, message: str = "Неизвестная ошибка"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class NotFoundError(TaskFlowException):
    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(message)


class ForbiddenError(TaskFlowException):
    def __init__(self, message: str = "Доступ запрещён"):
        super().__init__(message)


class ConflictError(TaskFlowException):
    def __init__(self, message: str = "Ресурс уже существует"):
        super().__init__(message)


class NotAuthorizedError(TaskFlowException):
    def __init__(self, message: str = "Требуется авторизация"):
        super().__init__(message)


class RepositoryError(TaskFlowException):
    def __init__(self, message: str = "Связанная запись не найдена"):
        super().__init__(message)
