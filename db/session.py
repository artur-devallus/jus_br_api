from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from lib.json_utils import default_json_encoder

engine = create_engine(
    settings.DATABASE_URL, pool_pre_ping=True, future=True, pool_recycle=3600, json_serializer=default_json_encoder
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
