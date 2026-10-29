from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DASHBOARD_", env_file=_PROJECT_DIR / ".env")

    # Must match src/main.cpp
    mqtt_broker: str = "broker.hivemq.com"
    mqtt_port: int = 1883
    mqtt_topic: str = "bingus-sic-6767420/sensors"

    # Must match get_status() in src/main.cpp
    gas_threshold: float = 3830
    temp_high_threshold: float = 50.0
    humidity_low_threshold: float = 40.0

    db_path: Path = _PROJECT_DIR / "karhutla.db"
    web_dir: Path = _PROJECT_DIR / "web"


@lru_cache
def get_settings() -> Settings:
    return Settings()
