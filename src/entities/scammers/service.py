from src.entities.scammers.schemas import ScammerScheme
from src.repository import RepositoryInterface, IntegrityException
from src.entities.scammers.models import scammers_repository


class ScammerService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def get_scammer(self, user_id: int):
        return await self.repository.get(user_id)

    async def add_scammer(self, scammer: ScammerScheme):
        try:
            await self.repository.create(scammer.model_dump())
        except IntegrityException:
            scammer_db = await self.repository.get(scammer.id)
            data = {"id": scammer.id, "number_requests": scammer_db.number_requests + 1}
            await scammers_repository.update(data, scammer_db.id)


scammers_service = ScammerService(scammers_repository)
