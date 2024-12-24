from datetime import datetime

from sqlalchemy import text

from src.core.schemas.scammer import ScammerScheme
from src.core.schemas.proof import ProofScheme
from src.db.database import async_session_maker
from src.db.errors import DBError
from src.db.models import Scammer, Proof, ScammerMedia
from src.db.repository import RepositoryInterface


scammers_repository = Scammer.repository()
proof_repository = Proof.repository()
media_repository = ScammerMedia.repository()


class ScammerService:

    def __init__(
            self,
            repository: RepositoryInterface,
            proof_repository_: RepositoryInterface,
            scammer_media_repository: RepositoryInterface
    ):
        self.repository = repository
        self.proof_repository = proof_repository_
        self.scammer_media_repository = scammer_media_repository

    async def get_scammer_list(self):
        return await self.repository.get_list(self.repository.model.is_scam == True)

    async def get_scammer_by_all(self, user_id: int, username: str):
        scammer_by_id = await self.repository.get(user_id)
        scammer_by_username = await self.repository.get_by(username=username)

        if scammer_by_id:
            return scammer_by_id
        elif scammer_by_username:
            return scammer_by_username
        else:
            return None

    async def get_scammer(self, user_id: int):
        return await self.repository.get(user_id)

    async def get_scammer_by_username(self, username: str):
        return await self.repository.get_by(username=username)

    async def get_by_scammer_id(self, scammer_id: int):
        return await self.repository.get_by(scammer_id=scammer_id)

    async def add_scammer(self, scammer: ScammerScheme):
        try:
            return await self.repository.create(scammer.model_dump())
        except DBError:
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

    async def save(self, scammer: ScammerScheme, proof: ProofScheme, media: list, decision: bool = False, moderator_id: int = None):
        try:
            scammer_from_db = await self.repository.create(scammer.model_dump())
        except DBError as e:
            print(e)
            scammer_from_db = await self.repository.update(scammer.model_dump(), scammer.id)

        proof_data = proof.model_dump()
        proof_data["decision"] = decision
        if moderator_id:
            proof_data["moderator_id"] = moderator_id

        del proof_data["id"]

        proof_from_db = await self.proof_repository.create(proof_data)

        for i, media_item in enumerate(media):
            media[i]["scammer_id"] = scammer_from_db.id
            media[i]["proof_id"] = proof_from_db.id

        if media:
            await self.scammer_media_repository.create_many(media)

        return scammer_from_db, proof_from_db

    # todo: move to service
    async def get_last_true_proofs(self, scammer_id: int):
        sql_query = text(f'''
            SELECT srm.*
            FROM media srm
            JOIN (
                SELECT scammer_id, MAX(proof_id) AS max_reports_id
                FROM media
                WHERE scammer_id = {scammer_id}
                GROUP BY scammer_id
            ) max_reports ON srm.scammer_id = max_reports.scammer_id AND srm.proof_id = max_reports.max_reports_id
            JOIN proofs sr ON srm.scammer_id = sr.scammer_id AND sr.decision = true;
        ''')
        async with async_session_maker() as session:
            result = await session.execute(sql_query)
            scammer_report_media = result.all()
            print("-" * 100)
            print(scammer_report_media)
            print("-" * 100)
            return scammer_report_media


scammers_service = ScammerService(scammers_repository, proof_repository, media_repository)
