import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings
from app.utils.json import to_jsonable


def _json_serializer(value):
    """Serialize JSON columns after converting NumPy values to native types."""
    return json.dumps(to_jsonable(value), ensure_ascii=False)


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    json_serializer=_json_serializer,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
