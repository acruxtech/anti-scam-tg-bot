from pydantic import BaseModel


class UserInfoScheme(BaseModel):
    id: int
    username: str
    link: str
