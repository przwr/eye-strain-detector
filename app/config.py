"""Centralised settings loaded from environment / .env via pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    camera_index: int = 0
    db_url: str = "sqlite:///./eyestrain.db"
    low_blink_rate: float = 12.0
    perclos_warn: float = 0.20
    break_interval_min: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
