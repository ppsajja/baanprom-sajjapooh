"""สร้างทุกตารางตาม models.py (T-01) ระบบจริงใช้ Alembic ได้ภายหลัง"""
from app.db.session import Base
from app.db import models  # noqa: F401  ให้ SQLAlchemy เห็นทุกตารางก่อน create_all


def upgrade(engine) -> None:
    Base.metadata.create_all(engine)
