from datetime import datetime

from sqlalchemy import text

from src.db.database import async_session_maker
from src.db.errors import DBError
from src.db.repository import RepositoryInterface

from src.db.models import User
from src.core.schemas.user import UserScheme


class UserService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_user(self, user: UserScheme):
        try:
            await self.repository.create(user.model_dump())
        except DBError:
            update_user = user.model_dump()
            update_user["datetime_last"] = datetime.now()
            await self.repository.update(update_user, user.id)

    async def update_user_status(self, user_id: int, is_blocked: bool):
        data = {"is_blocked": is_blocked}
        await self.repository.update(data, user_id)

    # todo: move to repository
    async def count_users(self) -> tuple[int]:
        """Return misc counts about users

        Returns:
            tuple[int]: (total_amount, new_amount, blocked_users, active_users)
        """
        sql_query = text(
            """
                SELECT
                (SELECT COUNT(*) FROM users)
                    AS total_records,
                (SELECT  COUNT(*) FROM users WHERE datetime_first >= NOW() - '1 day'::INTERVAL)
                    AS records_last_24_hours,
                (SELECT COUNT(*) FROM users WHERE is_blocked=true)
                    AS blocked_records;
            """
        )
        async with async_session_maker() as session:
            result = await session.execute(sql_query)

        data = result.all()
        data = data[0]
        count, count24, blocked_count = data
        return count, count24, blocked_count, count - blocked_count


user_service = UserService(User.repository())
