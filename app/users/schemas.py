from datetime import datetime
from fastapi_users import schemas
from pydantic import BaseModel

class UserRead(schemas.BaseUser[int]):
    username: str
    is_premium: bool
    premium_end_at: datetime | None
    


class UserCreate(schemas.BaseUserCreate):
    password: str
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = None


class UserId(BaseModel):
    id: int

class UserCharge(BaseModel):
    id: int
    days: int