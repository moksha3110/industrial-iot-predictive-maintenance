from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./predictive_maintenance.db"
    sensor_timeout_seconds: int = 60
    simulation_interval_seconds: int = 5
    aws_region: str = ""
    sns_topic_arn: str = ""
    owner_email: str = ""
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

TEMP_WARNING, TEMP_CRITICAL = 70.0, 85.0
VIB_WARNING, VIB_CRITICAL = 4.0, 7.0
PRESSURE_NORMAL = (30.0, 80.0)
PRESSURE_CRITICAL = (20.0, 95.0)
PHYSICAL_BOUNDS = {"temperature": (-40, 200), "vibration": (0, 50), "pressure": (0, 300)}
VALID_SENSORS = {"temperature", "vibration", "pressure"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
