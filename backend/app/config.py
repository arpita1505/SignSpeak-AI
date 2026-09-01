"""Application configuration."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    # Application
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database
    database_url: str = ""  # Empty means use SQLite

    # ML Model
    model_path: str = "artifacts/signspeak_model.joblib"
    model_metadata_path: str = "artifacts/model_metadata.json"

    # Inference
    confidence_threshold: float = 0.75
    stability_window: int = 5
    stability_min_count: int = 4
    sign_cooldown_ms: int = 800

    # WebSocket
    max_websocket_message_bytes: int = 5_242_880

    # Logging
    log_level: str = "INFO"

    @property
    def db_url(self) -> str:
        """Get database URL, defaulting to SQLite if not set."""
        if self.database_url:
            return self.database_url.replace("postgres://", "postgresql://", 1)
        # Use SQLite in project root
        return "sqlite:///./signspeak.db"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def allowed_origins(self) -> list[str]:
        """Configured browser origins; production frontend normally uses the same origin."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
