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

    class Config:
        from_attributes = True

