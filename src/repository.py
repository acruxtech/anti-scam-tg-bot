from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete, text
from sqlalchemy.exc import IntegrityError

from src.database import async_session_maker, Base


class RepositoryInterface(ABC):

    def __init__(self, model):
        self.model = model

    @abstractmethod
    async def create(self, data: dict):
        raise NotImplemented

    @abstractmethod
    async def update(self, update_date: dict, entity_id: int):
        raise NotImplemented

    @abstractmethod
    async def get(self, entity_id: int):
        raise NotImplemented

    @abstractmethod
    async def get_list(self, *filters):
        raise NotImplemented

    @abstractmethod
    async def delete(self, model_id: int):
        raise NotImplemented

    @abstractmethod
    async def get_by_username(self, username: str):
        raise NotImplemented


class SQLAlchemyRepository(RepositoryInterface):

    def __init__(self, model: Base):
        self.model = model

    async def create(self, data: dict):
        async with async_session_maker() as session:
            stmt = insert(self.model).returning(self.model).values(**data)
            try:
                result = await session.execute(stmt)
            except IntegrityError:
                raise IntegrityException
            else:
                await session.commit()
                return result.scalar()

    async def create_many(self, data: list):
        async with async_session_maker() as session:
            stmt = insert(self.model).returning(self.model).values(data)
            try:
                result = await session.execute(stmt)
            except IntegrityError:
                raise IntegrityException
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

    async def get_by_scammer_id(self, scammer_id: int):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.scammer_id == scammer_id)
            result = await session.execute(query)
            return result.scalar()

    async def get_by_username(self, username: str):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.username == username)
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

    async def delete_by_scammer_report_id(self, scammer_report_id: int):
        async with async_session_maker() as session:
            stmt = delete(self.model).where(self.model.scammers_reports_id == scammer_report_id)
            await session.execute(
                f"DELETE FROM {self.model.__tablename__} WHERE scammers_reports_id = {scammer_report_id}"
            )
            await session.commit()

    async def get_last_true_proofs(self, scammer_id: int):
        sql_query = text('''
            SELECT srm.*
            FROM scammers_reports_media srm
            JOIN (
                SELECT scammer_id, MAX(scammers_reports_id) AS max_reports_id
                FROM scammers_reports_media
                WHERE (scammer_id, scammers_reports_id) IN (
                    SELECT scammer_id, MAX(scammers_reports_id) AS max_reports_id
                    FROM scammers_reports_media
                    WHERE decision = 1 AND scammer_id = :scammer_id
                    GROUP BY scammer_id
                )
                GROUP BY scammer_id
            ) max_reports ON srm.scammer_id = max_reports.scammer_id AND srm.scammers_reports_id = max_reports.max_reports_id;
        ''')
        async with async_session_maker() as session:
            result = await session.execute(sql_query, scammer_id=scammer_id)
            scammer_report_media = result.scalars().all()
            print("-" * 100)
            print(scammer_report_media)
            print("-" * 100)
            return scammer_report_media


class IntegrityException(Exception):
    pass
