
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
