from datetime import datetime

from src.db.errors import DBError
from src.db.repository import RepositoryInterface

from src.db.models import UserInfo
from src.core.schemas import UserInfoScheme


class UserInfoService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_user_info(self, user: UserInfoScheme):
        try:
            await self.repository.create(user.model_dump())
        except DBError:
            update_user = user.model_dump()
            update_user["datetime_last"] = datetime.now()
            await self.repository.update(update_user, user.id)

    async def get_user_info_by_id(self, _id: int):
        return await self.repository.get_by(id=_id)

    async def get_user_info_by_username(self, username: str):
        return await self.repository.get_by(username=username)


user_info_service = UserInfoService(UserInfo.repository())
