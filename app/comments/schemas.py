# comments/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List

class CommentCreate(BaseModel):
    content: str
    article_id: str
    parent_id: int | None = None

class CommentRead(BaseModel):
    id: int
    content: str
    user_id: int
    article_id: str
    created_at: datetime
    parent_id: int | None = None
    username: str | None = None # ⭐ 新增字段：用户名
    like_count: int = 0
    liked: bool = False 
    replies: List["CommentRead"] = []  # ⬅️ 加上这句

    class Config:
        from_attributes = True

class CommentDelete(BaseModel):
    id: int

# 解决 forward reference
CommentRead.model_rebuild()