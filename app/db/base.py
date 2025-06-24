from sqlalchemy.orm import DeclarativeBase
from app.db.session import engine


class Base(DeclarativeBase):
    pass
