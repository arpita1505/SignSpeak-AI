"""Database configuration and setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Create engine
if settings.database_url:
    engine = create_engine(
        settings.db_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.db_url else {},
    )
else:
    engine = create_engine("sqlite:///./signspeak.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import models to register them with Base
# This must come after Base is defined
from app.models.translation import TranslationHistory  # noqa: F401


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
