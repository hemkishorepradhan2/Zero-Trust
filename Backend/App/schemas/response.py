from pydantic import BaseModel

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

class RiskResponse(BaseModel):
    username: str
    endpoint: str
    risk_score: int
    decision: str
