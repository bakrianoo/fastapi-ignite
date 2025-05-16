"""
Application configuration management
"""
import os
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from pydantic import Field, PostgresDsn, RedisDsn, model_validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"


class GeneralSettings(BaseModel):
    debug: bool = False
    log_level: str = "INFO"
    project_name: str = "FastAPI-Ignite"
    project_description: str = "A FastAPI application"
    version: str = "0.1.0"
    
    # Override from environment variables
    @model_validator(mode='after')
    def override_from_env(self) -> "GeneralSettings":
        if "DEBUG" in os.environ:
            debug_val = os.environ["DEBUG"].lower()
            self.debug = debug_val == "true"
        if "LOG_LEVEL" in os.environ:
            self.log_level = os.environ["LOG_LEVEL"]
        if "PROJECT_NAME" in os.environ:
            self.project_name = os.environ["PROJECT_NAME"]
        if "PROJECT_DESCRIPTION" in os.environ:
            self.project_description = os.environ["PROJECT_DESCRIPTION"]
        if "VERSION" in os.environ:
            self.version = os.environ["VERSION"]
        return self


class ApiSettings(BaseModel):
    prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Override from environment variables
    @model_validator(mode='after')
    def override_from_env(self) -> "ApiSettings":
        if "API_PREFIX" in os.environ:
            self.prefix = os.environ["API_PREFIX"]
        if "HOST" in os.environ:
            self.host = os.environ["HOST"]
        if "PORT" in os.environ:
            self.port = int(os.environ["PORT"])
        return self


class CorsSettings(BaseModel):
    origins: List[str] = ["*"]
    
    # Override from environment variables
    @model_validator(mode='after')
    def override_from_env(self) -> "CorsSettings":
        if "CORS_ORIGINS" in os.environ:
            import json
            try:
                self.origins = json.loads(os.environ["CORS_ORIGINS"])
            except json.JSONDecodeError:
                # Fallback to a single origin if not valid JSON
                self.origins = [os.environ["CORS_ORIGINS"]]
        return self


class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "app_db"
    
    # Override from environment variables
    @model_validator(mode='after')
    def override_from_env(self) -> "DatabaseSettings":
        # Check for environment variable overrides
        env_prefix = "POSTGRES_"
        if os.environ.get(f"{env_prefix}USER"):
            self.user = os.environ[f"{env_prefix}USER"]
        if os.environ.get(f"{env_prefix}PASSWORD"):
            self.password = os.environ[f"{env_prefix}PASSWORD"]
        if os.environ.get(f"{env_prefix}DB"):
            self.database = os.environ[f"{env_prefix}DB"]
        if os.environ.get(f"{env_prefix}HOST"):
            self.host = os.environ[f"{env_prefix}HOST"]
        if os.environ.get(f"{env_prefix}PORT"):
            self.port = int(os.environ[f"{env_prefix}PORT"])
        
        return self


class RedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6300
    password: str = ""
    db: int = 0
    
    # Override from environment variables
    @model_validator(mode='after')
    def override_from_env(self) -> "RedisSettings":
        # Check for environment variable override
        if os.environ.get("REDIS_HOST"):
            self.host = os.environ["REDIS_HOST"]
        if os.environ.get("REDIS_PASSWORD") is not None:  # Allow empty string
            self.password = os.environ["REDIS_PASSWORD"]
        if os.environ.get("REDIS_PORT"):
            self.port = int(os.environ["REDIS_PORT"])
        if os.environ.get("REDIS_DB"):
            self.db = int(os.environ["REDIS_DB"])
        return self


class DramatiqSettings(BaseModel):
    broker: str = "redis"
    processes: int = 2
    threads: int = 8
    
    # Override from environment variables
    @model_validator(mode='after')
    def override_from_env(self) -> "DramatiqSettings":
        if os.environ.get("DRAMATIQ_BROKER"):
            self.broker = os.environ["DRAMATIQ_BROKER"]
        if os.environ.get("DRAMATIQ_PROCESSES"):
            self.processes = int(os.environ["DRAMATIQ_PROCESSES"])
        if os.environ.get("DRAMATIQ_THREADS"):
            self.threads = int(os.environ["DRAMATIQ_THREADS"])
        return self


class CacheSettings(BaseModel):
    ttl_seconds: int = 300
    backend_type: str = "redis"  # Options: "redis", "file", "memory"
    file_path: str = "cache"  # Path for file-based cache, relative to project root
    
    # Override from environment variables
    @model_validator(mode='after')
    def override_from_env(self) -> "CacheSettings":
        if os.environ.get("CACHE_BACKEND_TYPE"):
            self.backend_type = os.environ["CACHE_BACKEND_TYPE"]
        if os.environ.get("CACHE_TTL_SECONDS"):
            self.ttl_seconds = int(os.environ["CACHE_TTL_SECONDS"])
        if os.environ.get("CACHE_FILE_PATH"):
            self.file_path = os.environ["CACHE_FILE_PATH"]
        return self


class SchedulerSettings(BaseModel):
    enabled: bool = True  # Whether to enable the APScheduler
    
    # Override from environment variables
    @model_validator(mode='after')
    def override_from_env(self) -> "SchedulerSettings":
        if os.environ.get("SCHEDULER_ENABLED"):
            self.enabled = os.environ.get("SCHEDULER_ENABLED").lower() == "true"
        return self


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
            logging.debug(f"  - System environment variables")

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
