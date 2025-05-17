<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="/docs/assets/logo-main.png">
    <source media="(prefers-color-scheme: light)" srcset="/docs/assets/logo-main.png">
    <img alt="FastAPI-Ignite Boilerplate " src="/docs/assets/logo-main.png" width="158" height="326" style="max-width: 100%;">
  </picture>
  <br/>
</p>

<p align="center">
   <h2 align="center">FastAPI-Ignite Boilerplate </h2>
</p>

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
   ```bash
   git clone https://github.com/bakrianoo/fastapi-ignite.git
   cd fastapi-ignite
   ```

2. Set up environment:
   ```bash
   # Copy the example .env file and edit with your configuration
   cp .env.example .env
   ```

### Start with Docker:
   ```bash
   docker-compose up -d
   ```

### Setting up locally

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set up environment variables**:
   ```bash
   copy .env.example .env
   ```
   Edit the .env file with your configuration. All environment settings are now consolidated in this single file.

4. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

5. Start the API server
   ```bash
   python cli.py api --reload
   ```

6. Run database migrations
   ```bash
   python cli.py db migrate
   ```

7. Start the background worker
   ```bash
   python cli.py worker
   ```

8. Start the scheduler
   ```bash
   python cli.py scheduler
   ```

9. Access the API documentation:
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## Development

See [DEVELOPER GUIDE](DEVELOPER-GUIDE.md) for detailed development information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.