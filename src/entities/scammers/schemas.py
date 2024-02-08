from pydantic import BaseModel


class ScammerScheme(BaseModel):
    id: int
    username: str | None = None
    first_name: str | None = None
    language_code: str | None = None


class ProofScheme(BaseModel):
    id: int | None = None
    text: str
    scammer_id: int
    user_id: int


class ScammerReportSchemeBase(BaseModel):
    text: str
    reported_id: int
    scammer_id: int


class ScammerReportSchemeCreate(ScammerReportSchemeBase):
    pass


class ScammerAnsweredScheme(BaseModel):
    is_reviewed: bool
    reviewer_id: int
    decision: bool
    explanation: str | None = None
