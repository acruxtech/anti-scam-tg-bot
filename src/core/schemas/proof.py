from pydantic import BaseModel


class ProofScheme(BaseModel):
    id: int | None = None
    text: str
    scammer_id: int
    user_id: int

