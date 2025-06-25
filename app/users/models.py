from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db.base import Base
from app.comments.models import Comment

class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(length=32), nullable=False, server_default="temp")

    # 建立双向关系：一个用户对应多个评论
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
