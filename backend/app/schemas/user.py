from datetime import datetime
from pydantic.v1 import EmailStr, BaseModel


# -------- Base --------
class UserBase(BaseModel):
    full_name: str | None = None
    email: EmailStr


# -------- Create --------
class UserCreate(UserBase):
    password: str


# -------- Auth login --------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------- Out --------
class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
