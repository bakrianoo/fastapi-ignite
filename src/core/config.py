"""
Application configuration management
"""
import os
import logging
from functools import lru_cache
from pathlib import Path
from typing import List, Union, Optional

from pydantic import Field, PostgresDsn, RedisDsn, BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"


class GeneralSettings(BaseModel):
    debug: bool = os.environ.get("DEBUG", "False")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    project_name: str = os.environ.get("PROJECT_NAME", "FastAPI-Ignite")
    project_description: str = os.environ.get("PROJECT_DESCRIPTION", "A FastAPI application")
    version: str = os.environ.get("VERSION", "0.1.0")
    
    # Override from environment variables
    @field_validator("debug", mode="before")
    def parse_debug(cls, value: Union[str, bool]) -> bool:
        if isinstance(value, str):
            return value.lower() == "true"
        return value


class ApiSettings(BaseModel):
    prefix: str = os.environ.get("API_PREFIX", "/api")
    host: str = os.environ.get("HOST", "0.0.0.0")
    port: int = int(os.environ.get("PORT", 8000))


class CorsSettings(BaseModel):
    origins: List[str] = os.environ.get("CORS_ORIGINS", ["*"])
    
    # Override from environment variables
    @field_validator("origins", mode="before")
    def parse_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [value]
        return value


class DatabaseSettings(BaseModel):
    host: str = os.environ.get("POSTGRES_HOST", "localhost")
    port: int = int(os.environ.get("POSTGRES_PORT", 5432))
    user: str = os.environ.get("POSTGRES_USER", "postgres")
    password: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    database: str = os.environ.get("POSTGRES_DB", "app_db")


class RedisSettings(BaseModel):
    host: str = os.environ.get("REDIS_HOST", "localhost")
    port: int = int(os.environ.get("REDIS_PORT", 6300))
    password: str = os.environ.get("REDIS_PASSWORD", "")
    db: int = int(os.environ.get("REDIS_DB", 0))


class DramatiqSettings(BaseModel):
    broker: str = os.environ.get("DRAMATIQ_BROKER", "redis")
    processes: int = int(os.environ.get("DRAMATIQ_PROCESSES", 2))
    threads: int = int(os.environ.get("DRAMATIQ_THREADS", 8))


class CacheSettings(BaseModel):
    ttl_seconds: int = int(os.environ.get("CACHE_TTL_SECONDS", 300))
    backend_type: str = os.environ.get("CACHE_BACKEND_TYPE", "redis")  # Options: "redis", "file", "memory"
    file_path: str = os.environ.get("CACHE_FILE_PATH", "cache")  # Path for file-based cache, relative to project root


class SchedulerSettings(BaseModel):
    enabled: bool = os.environ.get("SCHEDULER_ENABLED", True)  # Whether to enable the APScheduler
    
    # Override from environment variables
    @field_validator("enabled", mode="before")
    def parse_enabled(cls, value: Union[str, bool]) -> bool:
        if isinstance(value, str):
            return value.lower() == "true"
        return value


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Config model for Pydantic
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # ignore extra environment variables
    )
    
    # Environment setting
    ENV: str = Field("development", description="Environment name")
    
    # Nested settings models
    general: GeneralSettings = GeneralSettings()
    api: ApiSettings = ApiSettings()
    cors: CorsSettings = CorsSettings()
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    dramatiq: DramatiqSettings = DramatiqSettings()
    cache: CacheSettings = CacheSettings()
    scheduler: SchedulerSettings = SchedulerSettings()
    
    # Computed properties
    DATABASE_URI: Optional[PostgresDsn] = None
    REDIS_URI: Optional[RedisDsn] = None
    
    def __init__(self, **data):
        """Initialize settings from environment variables"""
        # Initialize with the data from environment variables
        super().__init__(**data)
        
        # Construct database and Redis URIs
        self.DATABASE_URI = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.database.user,
            password=self.database.password,
            host=self.database.host,
            port=self.database.port,
            path=f"{self.database.database}",
        )
            
        self.REDIS_URI = RedisDsn.build(
            scheme="redis",
            host=self.redis.host,
            port=self.redis.port,
            password=self.redis.password or None,
            path=f"{self.redis.db}",
        )
        
        # Log config sources in debug mode
        if self.general.debug:
            logging.debug("Configuration loaded from:")
            logging.debug(f"  - Environment variables (.env file at: {ENV_FILE})")
            logging.debug("  - System environment variables")

    # Legacy uppercase aliases for nested settings
    @property
    def PROJECT_NAME(self) -> str:
        return self.general.project_name

    @property
    def PROJECT_DESCRIPTION(self) -> str:
        return self.general.project_description

    @property
    def VERSION(self) -> str:
        return self.general.version

    @property
    def LOG_LEVEL(self) -> str:
        return self.general.log_level

    @property
    def DEBUG(self) -> bool:
        return self.general.debug

    @property
    def API_PREFIX(self) -> str:
        return self.api.prefix

    @property
    def HOST(self) -> str:
        return self.api.host

    @property
    def PORT(self) -> int:
        return self.api.port

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.cors.origins

    @property
    def POSTGRES_USER(self) -> str:
        return self.database.user

    @property
    def POSTGRES_PASSWORD(self) -> str:
        return self.database.password

    @property
    def POSTGRES_HOST(self) -> str:
        return self.database.host

    @property
    def POSTGRES_PORT(self) -> int:
        return self.database.port

    @property
    def POSTGRES_DB(self) -> str:
        return self.database.database

    @property
    def REDIS_HOST(self) -> str:
        return self.redis.host

    @property
    def REDIS_PORT(self) -> int:
        return self.redis.port

    @property
    def REDIS_DB(self) -> int:
        return self.redis.db
    
    @property
    def REDIS_PASSWORD(self) -> str:
        """Legacy alias for Redis password"""
        return self.redis.password

    @property
    def DRAMATIQ_BROKER(self) -> str:
        return self.dramatiq.broker

    @property
    def DRAMATIQ_PROCESSES(self) -> int:
        return self.dramatiq.processes

    @property
    def DRAMATIQ_THREADS(self) -> int:
        return self.dramatiq.threads
        
    @property
    def SCHEDULER_ENABLED(self) -> bool:
        return self.scheduler.enabled

    @property
    def CACHE_TTL_SECONDS(self) -> int:
        """Legacy alias for cache TTL seconds"""
        return self.cache.ttl_seconds
        
    @property
    def CACHE_BACKEND_TYPE(self) -> str:
        """The type of cache backend to use"""
        return self.cache.backend_type
        
    @property
    def CACHE_FILE_PATH(self) -> str:
        """Path for file-based cache storage"""
        from pathlib import Path
        base_path = Path(__file__).parent.parent.parent
        return str(base_path / self.cache.file_path)


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache a Settings instance
    """
    return Settings()


# Create a non-cached instance to allow runtime modifications
settings = Settings()
