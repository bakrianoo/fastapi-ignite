# Developer Guide

This document provides guidance for developers working on FastAPI-Ignite Boilerplate  project. It covers the architecture, development workflow, and best practices.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Development Environment Setup](#development-environment-setup)
- [Database Management](#database-management)
- [API Development](#api-development)
- [Background Tasks](#background-tasks)
- [Scheduled Tasks](#scheduled-tasks)
- [Caching](#caching)
- [Testing](#testing)
- [Docker Development](#docker-development)
- [Deployment](#deployment)

## Architecture Overview

FastAPI-Ignite FastAPI Boilerplate  is built with a clean architecture design that separates concerns into distinct layers:

1. **API Layer**: Handles HTTP requests/responses using FastAPI
2. **Service Layer**: Contains business logic
3. **Repository Layer**: Handles data access through SQLAlchemy
4. **Domain Layer**: Core business entities and logic

The application also employs several subsystems:
- **Task Queue**: Dramatiq for background task processing
- **Scheduler**: APScheduler for periodic tasks
- **Cache**: Multi-backend caching system (Redis, File, Memory)
- **Config**: Environment variable based configuration
  
### Configuration Loading
When the application starts (via `get_settings()` in `src/core/config.py`), settings are loaded from:
1. Environment variables (including from `.env`)
  
The settings are cached and drive application behavior.

## Project Structure

```
fastapi-ignite/
│
├── alembic/                         # Database migrations
│
├── src/                             # Application source code
│   ├── api/                         # API routes and dependencies
│   │   ├── v1/                      # API version 1
│   │   │   ├── endpoints/           # API endpoints by resource
│   │   │   └── router.py            # v1 router configuration
│   │   └── deps.py                  # Shared API dependencies
│   │
│   ├── cache/                       # Caching utilities
│   │   ├── backends/                # Cache backend implementations
│   │   │   ├── base.py              # Abstract base class
│   │   │   ├── redis.py             # Redis backend
│   │   │   ├── file.py              # File-based backend
│   │   │   ├── memory.py            # In-memory backend
│   │   │   └── factory.py           # Cache backend factory
│   │   ├── dependencies.py          # Cache dependency provider
│   │   └── decorators.py            # Caching decorators
│   │
│   ├── core/                        # Core application code
│   │   ├── config.py                # Configuration management
│   │   ├── events.py                # Startup/shutdown events
│   │   ├── exceptions.py            # Exception handling
│   │   └── logging.py               # Logging configuration
│   │
│   ├── db/                          # Database models and sessions
│   │   ├── base.py                  # Base SQLAlchemy models
│   │   ├── session.py               # Database session management
│   │   └── models/                  # SQLAlchemy models
│   │
│   ├── schedulers/                  # Scheduled tasks
│   │   ├── jobs.py                  # Scheduled job definitions
│   │   └── scheduler.py             # APScheduler configuration
│   │
│   ├── schemas/                     # Pydantic schemas
│   ├── services/                    # Business logic services
│   ├── tasks/                       # Background tasks
│   └── utils/                       # Utility functions
│
├── tests/                           # Test suite
├── .env.example                     # Example environment variables
├── alembic.ini                      # Alembic configuration
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                       # Docker build configuration
├── main.py                          # Application entry point
├── requirements.txt                 # Project dependencies
└── requirements-dev.txt             # Development dependencies
```

## Development Environment Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis

### Setting up locally

1. **Clone the repository**:
   ```cmd
   git clone https://github.com/bakrianoo/fastapi-ignite
   cd fastapi-ignite
   ```

2. **Create a virtual environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**:
   ```cmd
   copy .env.example .env
   ```
   Edit the .env file with your configuration. All environment settings are now consolidated in this single file.

5. **Run database migrations**:
   ```cmd
   alembic upgrade head
   ```

6. Start the API server
   ```bash
   python cli.py api --reload
   ```

7. Run database migrations
   ```bash
   python cli.py db migrate
   ```

8. Start the background worker
   ```bash
   python cli.py worker
   ```

9. Start the scheduler
   ```bash
   python cli.py scheduler
   ```

### VS Code Configuration

For VS Code users, here's a recommended `settings.json` configuration:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.nosetestsEnabled": false
}
```

## Database Management

### Models

SQLAlchemy models are defined in `src/db/models/`. Each model should inherit from the base classes in `src/db/base.py`:

```python
from src.db.base import Base, TableNameMixin, TimestampMixin, UUIDMixin

class YourModel(Base, UUIDMixin, TableNameMixin, TimestampMixin):
    # Define your model here
    name = Column(String, index=True)
```

### Migrations

We use Alembic for database migrations:

1. **Create a new migration**:
   ```cmd
   alembic revision --autogenerate -m "description of changes"
   ```

2. **Apply migrations**:
   ```cmd
   alembic upgrade head
   ```

3. **Downgrade migrations**:
   ```cmd
   alembic downgrade -1
   ```

## API Development

### Creating a New API Endpoint

1. **Define a Pydantic schema** in `src/schemas/`:
   ```python
   from pydantic import BaseModel, Field

   class ItemBase(BaseModel):
       name: str = Field(..., description="Item name")
       description: str | None = Field(None, description="Item description")
   
   class ItemCreate(ItemBase):
       pass
   
   class ItemResponse(ItemBase):
       id: uuid.UUID
       created_at: datetime
   
       model_config = {"from_attributes": True}
   ```

2. **Create a service** in `src/services/`:
   ```python
   class ItemService:
       @staticmethod
       async def create_item(db: AsyncSession, item_data: ItemCreate) -> Item:
           # Service logic
   ```

3. **Add an API endpoint** in `src/api/v1/endpoints/`:
   ```python
   @router.post("/", response_model=ItemResponse)
   async def create_item(item_data: ItemCreate, db: AsyncSession = Depends(get_db_session)):
       return await ItemService.create_item(db, item_data)
   ```

4. **Register the router** in `src/api/v1/router.py`:
   ```python
   from src.api.v1.endpoints import your_endpoint
   router.include_router(your_endpoint.router)
   ```

### API Versioning

Each API version has its own directory (`v1`, `v2`, etc.) with separate routers and endpoints. This allows for multiple API versions to coexist.

### API Documentation
FastAPI automatically exposes interactive docs for every version:
- **Swagger UI**: `http://<host>:<port>{{settings.API_PREFIX}}/docs` (e.g. `http://localhost:8000/api/docs`)
- **ReDoc**: `http://<host>:<port>{{settings.API_PREFIX}}/redoc` (e.g. `http://localhost:8000/api/redoc`)
- **OpenAPI schema JSON**: `http://<host>:<port>{{settings.API_PREFIX}}/openapi.json`

These paths come from the `docs_url`, `redoc_url`, and `openapi_url` parameters in `create_application()` (see `main.py`).

## Background Tasks

### Adding a New Background Task

1. **Define a task** in `src/tasks/jobs.py`:
   ```python
   @dramatiq.actor(
       queue_name="default",
       max_retries=3,
       time_limit=60000,
   )
   def process_something(item_id: str) -> Dict:
       # Task implementation
   ```

2. **Call the task** from your service or API:
   ```python
   from src.tasks.jobs import process_something
   
   # Call the task
   process_something.send(str(item_id))
   ```

3. **Run the worker** to process tasks:
   ```cmd
   python -m dramatiq src.tasks.jobs
   ```

## Scheduled Tasks

### Adding a New Scheduled Task

1. **Define a scheduled job** in `src/schedulers/jobs.py`:
   ```python
   async def your_scheduled_job():
       # Job implementation
   ```

2. **Register the job** in the `setup_jobs` function:
   ```python
   def setup_jobs(scheduler: AsyncIOScheduler) -> None:
       # Add your job
       scheduler.add_job(
           your_scheduled_job,
           trigger="interval",
           hours=1,
           id="your_job_id",
           replace_existing=True,
       )
   ```

### Enabling and Disabling the Scheduler

FastAPI-Ignite FastAPI Boilerplate  allows you to control whether the APScheduler runs or not using several methods:

#### Environment Configuration

You can enable or disable the scheduler in the .env file:

```
# Scheduler settings
SCHEDULER_ENABLED=true  # Set to false to disable the scheduler
```

#### Command Line Interface

When using the CLI, you can override the scheduler setting:

1. **When running the API server**:
   ```cmd
   # Enable the scheduler (regardless of config setting)
   python cli.py api --scheduler-enabled
   
   # Disable the scheduler (regardless of config setting)
   python cli.py api --scheduler-disabled
   ```

2. **When running the scheduler directly**:
   ```cmd
   # Enable the scheduler (regardless of config setting)
   python cli.py scheduler --enabled
   
   # Disable the scheduler (regardless of config setting)
   python cli.py scheduler --disabled
   ```

#### Environment Variables

You can also control the scheduler with environment variables:

```cmd
# Enable the scheduler
set SCHEDULER_ENABLED=true
python cli.py api

# Disable the scheduler
set SCHEDULER_ENABLED=false
python cli.py api
```

This is useful for deployment environments where you might want to run the scheduler on only one instance of your application.

## Caching

FastAPI-Ignite FastAPI Boilerplate supports multiple cache backends that can be configured through environment variables or configuration files. For detailed information on caching, see [Cache Documentation](docs/cache.md).

### Available Cache Backends

The application supports three different cache backends:

1. **Redis** - Default, distributed cache for production environments
2. **File** - Persistent file-based cache for single-server deployments
3. **Memory** - In-memory cache for development and testing

### Configuring Cache Backends

You can configure which cache backend to use through the following settings:

```
# In .env or environment variables
CACHE_BACKEND_TYPE=redis   # Options: "redis", "file", "memory"
CACHE_TTL_SECONDS=300      # Default TTL for cached items
CACHE_FILE_PATH=cache      # Path for file-based cache (relative to project root)
```

Configure in your .env file:

```
# Cache settings
CACHE_BACKEND_TYPE=redis  # Options: redis, file, memory
CACHE_TTL_SECONDS=300
CACHE_FILE_PATH=cache  # Used only with file backend
```

### Recommended Cache Backends for Different Environments

- **Development**: Use "memory" backend for faster startup and no external dependencies
- **Testing**: Use "memory" backend for test isolation
- **Staging**: Use "redis" or "file" depending on your infrastructure
- **Production**: Use "redis" for scalable, distributed caching

### Basic Usage Patterns

Here are the three main ways to use the caching system:

#### 1. Function-Level Caching with Decorators

```python
from src.cache.decorators import cached

@cached(ttl=300, key_prefix="user")
async def get_user(user_id: str) -> Dict:
    # Function implementation - result will be automatically cached
    return user_data
```

#### 2. Cache Invalidation with Decorators

```python
from src.cache.decorators import invalidate_cache

@invalidate_cache(key_pattern="user:*")
async def update_user(user_id: str, data: Dict) -> Dict:
    # After this function completes, matching cache keys will be invalidated
    return updated_user
```

#### 3. Direct Cache Access in Endpoints

```python
from src.cache import CacheBackend, get_cache
from fastapi import Depends

@router.get("/items/{item_id}")
async def get_item(item_id: str, cache: CacheBackend = Depends(get_cache)):
    # Manual cache handling gives you more control
    cache_key = f"item:{item_id}"
    
    # Try to get from cache first
    cached_item = await cache.get(cache_key)
    if cached_item:
        return json.loads(cached_item)
    
    # Get from database if not in cache
    item = await get_item_from_db(item_id)
    
    # Store in cache for future requests
    await cache.set(cache_key, json.dumps(item), ex=300)
    return item
```

For more detailed examples and advanced usage, refer to the [Cache Documentation](docs/cache.md).

### Cache Best Practices

1. **Use consistent key prefixes** for related items (e.g., `user:123`, `user:settings:123`)
2. **Set appropriate TTLs** based on data volatility and access patterns
3. **Implement proper cache invalidation** when data changes
4. **Handle cache misses gracefully** with fallback to database queries
5. **Serialize data consistently** (typically using JSON)
6. **Consider cache stampedes** for high-traffic applications

For detailed information on cache implementation, advanced usage patterns, and performance considerations, see the [Cache Documentation](docs/cache.md).

## Testing

### Running Tests

We use pytest for testing:

```cmd
pytest
```

Run with coverage:

```cmd
pytest --cov=src
```

### Writing Tests

1. **API Tests** go in `tests/test_api/`
2. **Service Tests** go in `tests/test_services/`
3. **Model Tests** go in `tests/test_models/`

Example test:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    response = await client.post(
        "/api/v1/items/",
        json={"name": "Test Item", "description": "Test Description"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"
```

## Docker Development

In the root `Dockerfile` we define two build stages:
1. **production** (aliased `production`) uses the base image and sets a `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]` without reload.  Build it with:
   ```cmd
   docker build --target production -t rankyx:prod .
   ```
2. **development** (the final stage) installs dev dependencies and sets a `CMD` with `--reload` for hot reloading.  Build or run it without specifying `--target`:
   ```cmd
   docker build -t rankyx:dev .
   ```

You can choose which image to run; the development image includes auto-reload, whereas the production image is lean and without reload.

### Starting the Docker environment

```cmd
docker-compose up -d
```

### Running commands in Docker

```cmd
docker-compose exec api alembic upgrade head
```

### Rebuilding after changes

```cmd
docker-compose build
docker-compose up -d
```

## Deployment

### Production Configuration

1. **Create a production environment file**:
   ```cmd
   copy .env.example .env.prod
   ```

2. **Update the production settings** with appropriate values for your production environment.

### Docker Production Deployment

Build and run production Docker containers:

```cmd
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Database Migrations in Production

Always back up your database before running migrations in production:

```cmd
# In the Docker container
docker-compose exec api alembic upgrade head
```

### Monitoring and Logging

In production, you can integrate the application with monitoring systems like Prometheus and logging solutions like ELK Stack or Datadog.

## Best Practices

1. **Follow PEP 8** for code style
2. **Write tests** for new features
3. **Document** your code with docstrings
4. **Type hint** all functions
5. **Validate data** with Pydantic
6. **Handle errors** gracefully
7. **Use async/await** consistently
8. **Log appropriately** at different levels
9. **Create migrations** for database changes
10. **Validate environment** before deployment
