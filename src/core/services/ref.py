from datetime import datetime

from src.core.schemas.ref import RefScheme
from src.db.errors import DBError
from src.db.models import Ref
from src.db.repository import RepositoryInterface


class RefService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_ref(self, ref: RefScheme):
        try:
            await self.repository.create(ref.model_dump())
        except DBError:
            update_ref = ref.model_dump()
            update_ref["datetime_last"] = datetime.now()
            await self.repository.update(update_ref, ref.id)

    async def delete_ref(self, _id: int):
        refs = await self.get_refs()
        return await self.repository.delete(refs[id].id)

    async def get_ref_by_title(self, title: str):
        return await self.repository.get_by(title=title)

    async def get_refs(self):
        return await self.repository.get_list()


ref_service = RefService(Ref.repository())
