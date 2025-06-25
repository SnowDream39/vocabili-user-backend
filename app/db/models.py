from sqlalchemy import ForeignKey, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTable

from sqlalchemy.orm import DeclarativeBase
from app.db.session import engine


class Base(DeclarativeBase):
    pass


class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[str] = mapped_column(String, index=True, server_default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('comment.id'), nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    # 关系字段
    user: Mapped["User"] = relationship("User", back_populates="comments")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="comment")

    parent: Mapped["Comment"] = relationship("Comment", remote_side=[id], backref="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete")    # 🔁 子评论（也就是回复）

class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(length=32), nullable=False, server_default="temp")

    # 建立双向关系：一个用户对应多个评论
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user")

from sqlalchemy import UniqueConstraint

class Like(Base):
    __tablename__ = 'like'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment_id: Mapped[int] = mapped_column(Integer, ForeignKey('comments.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[int] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="likes")
    comment: Mapped["Comment"] = relationship("Comment", back_populates="likes")

    __table_args__ = (
        UniqueConstraint('comment_id', 'user_id', name='like_user_id_IDX'),
    )
