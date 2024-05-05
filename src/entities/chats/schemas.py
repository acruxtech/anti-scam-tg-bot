from pydantic import BaseModel


class ChatScheme(BaseModel):
    id: int
    title: str
