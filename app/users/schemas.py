
from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    username: str
    is_premium: bool
    


class UserCreate(schemas.BaseUserCreate):
    password: str
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = None