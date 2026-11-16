from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enum import UserRole


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt chỉ nhận tối đa 72 byte
    phone: str | None = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    phone: str | None = None
    role: UserRole
    is_active: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut