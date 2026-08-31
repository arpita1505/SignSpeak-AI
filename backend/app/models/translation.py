"""Database models."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.database import Base


class TranslationHistory(Base):
    """Model for storing translation history."""

    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    model_version = Column(String)
    session_id = Column(String, index=True, nullable=True)
