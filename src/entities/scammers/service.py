from datetime import datetime

from src.entities.scammers.schemas import ScammerScheme, ScammerReportSchemeCreate, ScammerAnsweredScheme
from src.repository import RepositoryInterface, IntegrityException
from src.entities.scammers.models import scammers_repository, scammers_reports_repository


class ScammerService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def get_scammer_list(self):
        return await self.repository.get_list(self.repository.model.is_scam == True)

    async def get_scammer(self, user_id: int):
        return await self.repository.get(user_id)

    async def get_scammer_by_username(self, username: str):
        return await self.repository.get_by_username(username)

    async def add_scammer(self, scammer: ScammerScheme):
        try:
            return await self.repository.create(scammer.model_dump())
        except IntegrityException:
            scammer_db = await self.repository.get(scammer.id)
            data = {
                "id": scammer.id,
                "number_requests": scammer_db.number_requests + 1
            }
            data.update(scammer.model_dump())
            return await scammers_repository.update(data, scammer_db.id)

    async def update_username(self, scammer_id: int, username: str):
        data = {"username": username}
        await self.repository.update(data, scammer_id)

    async def confirm(self, scammer_id: int):
        data = {"is_scam": True, "datetime_confirmed": datetime.now()}
        await self.repository.update(data, scammer_id)

    async def delete_scammer(self, scammer_id: int):
        return await self.repository.delete(scammer_id)


class ScammerReportService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def update_scammer_report(self, scammer_report_id: int, message_id: int):
        pass

    async def create_scammer_report(self, scammer_report: ScammerReportSchemeCreate):
        return await self.repository.create(scammer_report.model_dump())

    async def answer_to_scammer_report(
            self, scammer_report_id: int, scammer_report_answer: ScammerAnsweredScheme
    ):
        data = {
            "is_reviewed": scammer_report_answer.is_reviewed,
            "datetime_reviewed": datetime.now(),
            "decision": scammer_report_answer.decision,
            "reviewer_id": scammer_report_answer.reviewer_id
        }

        if scammer_report_answer.explanation is not None:
            data.update({"explanation": scammer_report_answer.explanation})

        return await self.repository.update(data, scammer_report_id)

    async def get_scammer_report(self, scammer_report_id: int):
        return await self.repository.get(scammer_report_id)


scammers_service = ScammerService(scammers_repository)
scammers_reports_service = ScammerReportService(scammers_reports_repository)
