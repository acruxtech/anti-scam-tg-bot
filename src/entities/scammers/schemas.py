from pydantic import BaseModel


class ScammerScheme(BaseModel):
    id: int
    username: str | None = None
    first_name: str | None = None
    language_code: str | None = None
