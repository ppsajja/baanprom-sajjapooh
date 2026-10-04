"""สร้าง engine และ session ของ SQLAlchemy (ทีมเลือกเอง ไม่ได้มาจาก spec)"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

from app import config


class Base(DeclarativeBase):
    pass


def make_engine(url: str = config.DATABASE_URL):
    # SQLite ในหน่วยความจำต้องใช้ connection เดียวร่วมกันทุก session ไม่งั้นตารางหาย
    if url.startswith("sqlite"):
        return create_engine(
            url, connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
    return create_engine(url)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
