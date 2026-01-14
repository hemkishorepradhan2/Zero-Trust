from pydantic import BaseModel

class LoginRequest(BaseModel):
	username: str
	role: str
