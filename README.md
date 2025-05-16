<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/assets/main-logo.png">
    <source media="(prefers-color-scheme: light)" srcset="/assets/main-logo.png">
    <img alt="FastAPI-Ignite Boilerplate " src="/assets/main-logo.png" width="352" height="59" style="max-width: 100%;">
  </picture>
  <br/>
  <br/>
</p>

# FastAPI-Ignite Boilerplate 

**FastAPI-Ignite** Boilerplate is a production-ready FastAPI boilerplate application with a comprehensive set of features for modern web backend development.

## Core Technologies

- **FastAPI**: High-performance async web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM with async support
- **Pydantic v2**: Data validation and settings management using Python type hints
- **PostgreSQL**: Powerful open-source relational database
- **Redis**: In-memory data store for caching and message broker
- **Dramatiq**: Distributed task processing for background jobs
- **APScheduler**: Advanced Python scheduler for periodic tasks
- **Alembic**: Database migration tool

## Features

- ✅ **Modern Python codebase** using async/await syntax
- ✅ **Structured project layout** for maintainability
- ✅ **API versioning** to manage API evolution
- ✅ **Database integration** with async SQLAlchemy 2.0
- ✅ **Background task processing** with Dramatiq
- ✅ **Scheduled tasks** with APScheduler
- ✅ **Simple configuration** using environment variables
- ✅ **Comprehensive logging** with structured logs
- ✅ **Docker support** for easy deployment
- ✅ **Database migrations** with Alembic
- ✅ **Production-ready** with health checks, error handling, and more
- ✅ **Advanced caching** with multiple backends (Redis, File, Memory) at function and API endpoint levels

## Quick Start

1. Clone the repository:
   ```
   git clone https://github.com/your-org/FastAPI-Ignite-ai-engine.git
   cd FastAPI-Ignite-ai-engine
   ```

2. Set up environment:
   ```
   # Copy the example .env file and edit with your configuration
   cp .env.example .env
   ```

3. Start with Docker:
   ```
   docker-compose up -d
   ```

4. Or start locally:
   ```
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # for development

   # Run database migrations
   alembic upgrade head

   # Start the API server
   uvicorn main:app --reload
   ```

5. Access the API documentation:
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## Development

See [DEVELOPER GUIDE](DEVELOPER_GUIDE.md) for detailed development information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.