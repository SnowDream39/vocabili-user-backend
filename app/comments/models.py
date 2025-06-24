from sqlalchemy import ForeignKey, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.users.models import User  # 导入用户模型

class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[str] = mapped_column(String, index=True, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('comment.id'), nullable=True)


