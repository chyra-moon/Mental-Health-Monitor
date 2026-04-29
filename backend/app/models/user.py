from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=True)
    role = Column(Enum("student", "admin"), nullable=False, default="student")
    gender = Column(String(10), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
