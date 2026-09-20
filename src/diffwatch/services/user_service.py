from uuid import UUID

from diffwatch.daos.user_dao import UserDAO
from diffwatch.models.user_model import User


class UserService:
    def __init__(self, user_dao: UserDAO) -> None:
        self.user_dao = user_dao

    def create_user(self, user: User) -> UUID:
        return self.user_dao.create(user)