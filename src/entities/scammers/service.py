from src.entities.scammers.schemas import ScammerScheme, ScammerReportSchemeCreate
from src.repository import RepositoryInterface, IntegrityException
from src.entities.scammers.models import scammers_repository, scammers_reports_repository


class ScammerService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def get_scammer(self, user_id: int):
        return await self.repository.get(user_id)

    async def add_scammer(self, scammer: ScammerScheme):
        try:
            return await self.repository.create(scammer.model_dump())
        except IntegrityException:
            scammer_db = await self.repository.get(scammer.id)
            data = {"id": scammer.id, "number_requests": scammer_db.number_requests + 1}
            return await scammers_repository.update(data, scammer_db.id)


class ScammerReportService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def create_scammer_report(self, scammer_report: ScammerReportSchemeCreate):
        return await self.repository.create(scammer_report.model_dump())

    async def answer_to_scammer_report(self):
        pass
    async def get_scammer_report(self, scammer_report_id: int):
        return await self.repository.get(scammer_report_id)


scammers_service = ScammerService(scammers_repository)
scammers_reports_service = ScammerReportService(scammers_reports_repository)
