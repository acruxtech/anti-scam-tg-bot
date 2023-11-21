from pydantic import BaseModel


class UserScheme(BaseModel):
    id: int
    username: str
    first_name: str
    language_code: str | None = None
    is_premium: bool | None = None
    is_bot: bool | None = None
