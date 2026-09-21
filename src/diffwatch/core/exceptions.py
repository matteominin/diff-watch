from uuid import UUID

class DiffWatchError(Exception):
    """Base Exception"""

class ValidationError(DiffWatchError):
    """Base validation and invalid state error"""

class NotFoundError(DiffWatchError):
    """Not found base"""

class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")

class PlanNotFoundError(NotFoundError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"Plan not found for user: {user_id}")

class MonitorNotFoundError(NotFoundError):
    def __init__(self, id: UUID) -> None:
        super().__init__(f"Monitor not found: {id}")