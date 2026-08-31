"""Translation history endpoints."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.prediction import TranslationCreate, TranslationResponse
from app.services.history_service import HistoryService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[TranslationResponse])
async def get_history(
    limit: int = 100, db: Session = Depends(get_db)
) -> list[TranslationResponse]:
    """Get all translation history."""
    try:
        return HistoryService.get_all_history(db, limit=limit)
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")


@router.post("", response_model=TranslationResponse)
async def create_history(
    translation: TranslationCreate, db: Session = Depends(get_db)
) -> TranslationResponse:
    """Create a new translation history entry."""
    try:
        return HistoryService.create_history(db, translation)
    except Exception as e:
        logger.error(f"Error creating history: {e}")
        raise HTTPException(status_code=500, detail="Failed to create history")


@router.get("/{history_id}", response_model=Optional[TranslationResponse])
async def get_history_by_id(
    history_id: int, db: Session = Depends(get_db)
) -> TranslationResponse | None:
    """Get a specific translation history entry."""
    try:
        history = HistoryService.get_history_by_id(db, history_id)
        if not history:
            raise HTTPException(status_code=404, detail="History not found")
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")


@router.delete("/{history_id}")
async def delete_history(
    history_id: int, db: Session = Depends(get_db)
) -> dict:
    """Delete a translation history entry."""
    try:
        if not HistoryService.delete_history(db, history_id):
            raise HTTPException(status_code=404, detail="History not found")
        return {"message": "History deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting history: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete history")


@router.delete("")
async def delete_all_history(db: Session = Depends(get_db)) -> dict:
    """Delete all translation history."""
    try:
        HistoryService.delete_all_history(db)
        return {"message": "All history deleted"}
    except Exception as e:
        logger.error(f"Error deleting all history: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete history")
