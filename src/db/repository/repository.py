import logging
from typing import Type

from sqlalchemy import insert, select, update, delete, text
from sqlalchemy.exc import IntegrityError

from src.db.base import BaseModel
from src.db.errors import *
from src.db.repository import RepositoryInterface
from src.db.database import async_session_maker

logger = logging.getLogger(__name__)


class Repository(RepositoryInterface):

    def __init__(self, model: Type[BaseModel]):
        super().__init__(model)
        self.model = model

    async def create(self, data: dict):
        async with async_session_maker() as session:
            stmt = insert(self.model).returning(self.model).values(**data)
            try:
                result = await session.execute(stmt)
            except IntegrityError as e:
                logger.error(e)
                raise IntegrityException()
            else:
                await session.commit()
                return result.scalar()

    async def create_many(self, data: list):
        async with async_session_maker() as session:
            stmt = insert(self.model).returning(self.model).values(data)
            try:
                result = await session.execute(stmt)
            except IntegrityError:
                raise IntegrityException()
            else:
                await session.commit()
                return result

    async def get_list(self, *filters):
        async with async_session_maker() as session:
            stmt = select(self.model).filter(*filters)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get(self, entity_id: int):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.id == entity_id)
            result = await session.execute(query)
            return result.scalar()

    async def get_by(self, **kwargs):
        async with async_session_maker() as session:
            query = select(self.model)
            for key, value in kwargs.items():
                query = query.where(getattr(self.model, key) == value)
            result = await session.execute(query)
            return result.scalar()

    async def update(self, update_date: dict, entity_id: int):
        async with async_session_maker() as session:
            stmt = update(self.model).returning(self.model).where(self.model.id == entity_id).values(**update_date)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar()

    async def delete(self, model_id: int):
        async with async_session_maker() as session:
            stmt = delete(self.model).returning(self.model).where(self.model.id == model_id)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar()

#     async def delete_by_scammer_report_id(self, scammer_report_id: int):
#         async with async_session_maker() as session:
#             stmt = delete(self.model).where(self.model.scammers_reports_id == scammer_report_id)
#             await session.execute(stmt)
#             await session.commit()
