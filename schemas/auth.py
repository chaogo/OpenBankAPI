from pydantic import BaseModel


class Credential(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str