from abc import ABC, abstractmethod


class RepositoryInterface(ABC):

    def __init__(self, model):
        self.model = model

    @abstractmethod
    async def create(self, data: dict):
        raise NotImplemented

    @abstractmethod
    async def create_many(self, data: list):
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

    async def get_by(self, **kwargs):
        raise NotImplemented

    @abstractmethod
    async def delete(self, model_id: int):
        raise NotImplemented
