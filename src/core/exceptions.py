class TaskFlowException(Exception):
    pass


class NotFoundError(TaskFlowException):
    pass


class ForbiddenError(TaskFlowException):
    pass


class BadRequestError(TaskFlowException):
    pass
