from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
