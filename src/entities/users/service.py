from datetime import datetime

from src.repository import RepositoryInterface, IntegrityException

from src.entities.users.models import user_repository
from src.entities.users.schemas import UserScheme


class UserService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_user(self, user: UserScheme):
        try:
            await self.repository.create(user.model_dump())
        except IntegrityException:
            update_user = user.model_dump()
            update_user["datetime_last"] = datetime.now()
            await self.repository.update(update_user, user.id)


user_service = UserService(user_repository)
