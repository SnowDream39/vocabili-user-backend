# comments/schemas.py
from pydantic import BaseModel

class CommentCreate(BaseModel):
    content: str
    article_id: str
    parent_id: int | None = None

class CommentRead(BaseModel):
    id: int
    content: str
    user_id: int
    article_id: str
    parent_id: int | None = None
    username: str | None = None # ⭐ 新增字段：用户名

    class Config:
        from_attributes = True

