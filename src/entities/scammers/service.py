from src.repository import RepositoryInterface
from src.entities.scammers.models import scammers_repository


class ScammerService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def get_scammer(self, user_id: int):
        return await self.repository.get(user_id)


scammers_service = ScammerService(scammers_repository)
