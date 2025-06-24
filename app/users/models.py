from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db.base import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(length=32), nullable=False, server_default="temp")
