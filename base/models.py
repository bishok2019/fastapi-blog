from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.sql import func

from apps.database import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    updated_by = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)
