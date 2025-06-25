from pydantic import BaseModel

class LikeCreate(BaseModel):
    comment_id: int
    user_id: int

class LikeDelete(BaseModel):
    comment_id: int
    user_id: int

class LikeRead(BaseModel):
    comment_id: int
    user_id: int