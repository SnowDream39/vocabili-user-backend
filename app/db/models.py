from app.db.base import Base


from sqlalchemy import ForeignKey, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db.base import Base
#from app.users.models import User  # 导入用户模型

class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[str] = mapped_column(String, index=True, server_default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('comment.id'), nullable=True)

    # 关系字段
    user: Mapped["User"] = relationship("User", back_populates="comments")
    parent: Mapped["Comment"] = relationship("Comment", remote_side=[id], backref="replies")

class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(length=32), nullable=False, server_default="temp")

    # 建立双向关系：一个用户对应多个评论
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")

