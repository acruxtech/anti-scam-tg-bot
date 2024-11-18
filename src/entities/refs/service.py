from datetime import datetime

from src.db.repository import RepositoryInterface, IntegrityException

from src.entities.refs.models import Ref, ref_repository


class RefService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_ref(self, ref: Ref):
        try:
            await self.repository.create(ref.model_dump())
        except IntegrityException:
            update_ref = ref.model_dump()
            update_ref["datetime_last"] = datetime.now()
            await self.repository.update(update_ref, ref.id)


    async def delete_ref(self, id: int):
        refs = await self.get_refs()
        try:
            return await self.repository.delete(refs[id].id)
        except BaseException:
            ...

    async def get_ref_by_title(self, title: str):
        try:
            return await self.repository.get_by_title(title)
        except BaseException:
            ...

    async def get_refs(self):
        try:
            return await self.repository.get_list()
        except BaseException:
            ...



ref_service = RefService(ref_repository)
