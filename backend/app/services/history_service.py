"""Service for managing translation history."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models.translation import TranslationHistory
from app.schemas.prediction import TranslationCreate, TranslationResponse

logger = logging.getLogger(__name__)


class HistoryService:
    """Service for managing translation history."""

    @staticmethod
    def create_history(
        db: Session, translation: TranslationCreate, session_id: str | None = None
    ) -> TranslationResponse:
        """
        Create a new translation history entry.

        Args:
            db: Database session
            translation: Translation data
            session_id: Optional session ID

        Returns:
            Created translation object
        """
        try:
            db_translation = TranslationHistory(
                text=translation.text,
                model_version=translation.model_version,
                session_id=session_id,
            )
            db.add(db_translation)
            db.commit()
            db.refresh(db_translation)
            return db_translation
        except Exception as e:
            logger.error(f"Error creating translation history: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_all_history(db: Session, limit: int = 100) -> list[TranslationResponse]:
        """
        Get all translation history.

        Args:
            db: Database session
            limit: Maximum number of records

        Returns:
            List of translation records
        """
        try:
            return (
                db.query(TranslationHistory)
                .order_by(TranslationHistory.created_at.desc())
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Error fetching translation history: {e}")
            return []

    @staticmethod
    def get_history_by_id(db: Session, history_id: int) -> TranslationResponse:
        """
        Get a specific translation history entry.

        Args:
            db: Database session
            history_id: Translation ID

        Returns:
            Translation record or None
        """
        try:
            return db.query(TranslationHistory).filter(TranslationHistory.id == history_id).first()
        except Exception as e:
            logger.error(f"Error fetching translation: {e}")
            return None

    @staticmethod
    def delete_history(db: Session, history_id: int) -> bool:
        """
        Delete a translation history entry.

        Args:
            db: Database session
            history_id: Translation ID

        Returns:
            True if successful
        """
        try:
            db.query(TranslationHistory).filter(TranslationHistory.id == history_id).delete()
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting translation: {e}")
            db.rollback()
            return False

    @staticmethod
    def delete_all_history(db: Session) -> bool:
        """
        Delete all translation history.

        Args:
            db: Database session

        Returns:
            True if successful
        """
        try:
            db.query(TranslationHistory).delete()
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting all translations: {e}")
            db.rollback()
            return False
