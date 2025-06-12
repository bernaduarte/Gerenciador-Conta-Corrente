from pydantic import BaseModel

class LoginRequest(BaseModel):
    account_number: str
    password: str
class TokenResponse(BaseModel):
    access_token: str