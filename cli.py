"""
Command-line utility for running various components of the application
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

# load .env using dotenv
from dotenv import load_dotenv
load_dotenv()


def parse_args():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="FastAPI Boilerplate  command-line utilities",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # API server command
    api_parser = subparsers.add_parser("api", help="Run the API server")
    api_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    api_parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    api_parser.add_argument("--scheduler-enabled", action="store_true", dest="scheduler_enabled", 
                           default=None, help="Force enable the scheduler")
    api_parser.add_argument("--scheduler-disabled", action="store_false", dest="scheduler_enabled", 
                           default=None, help="Force disable the scheduler")
    
    # Worker command
    worker_parser = subparsers.add_parser("worker", help="Run the background task worker")
    worker_parser.add_argument("--processes", type=int, default=None, help="Number of worker processes")
    worker_parser.add_argument("--threads", type=int, default=None, help="Number of worker threads")
    
    
    # Scheduler command
    scheduler_parser = subparsers.add_parser("scheduler", help="Run the task scheduler")
    scheduler_parser.add_argument("--enabled", action="store_true", dest="scheduler_enabled", 
                                default=None, help="Force enable the scheduler")
    scheduler_parser.add_argument("--disabled", action="store_false", dest="scheduler_enabled", 
                                default=None, help="Force disable the scheduler")
    
    # DB command
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_subparsers = db_parser.add_subparsers(dest="db_command", help="Database command")
    
    # DB init command
    db_init_parser = db_subparsers.add_parser("init", help="Initialize the database")
    
    # DB migrate command
    db_migrate_parser = db_subparsers.add_parser("migrate", help="Run database migrations")
    db_migrate_parser.add_argument("--revision", type=str, default="head", help="Revision to migrate to")
    
    return parser.parse_args()


def run_api(args):
    """
    Run the API server
    """
    import uvicorn
    
    # Set environment variable for scheduler if specified
    if args.scheduler_enabled is not None:
        os.environ["SCHEDULER_ENABLED"] = str(args.scheduler_enabled).lower()
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.reload else "info",
    )


def run_worker(args):
    """
    Run the background task worker
    """
    from src.core.config import settings
    from src.tasks.worker import run_worker
    
    # Override settings if arguments provided
    if args.processes is not None:
        os.environ["DRAMATIQ_PROCESSES"] = str(args.processes)
    if args.threads is not None:
        os.environ["DRAMATIQ_THREADS"] = str(args.threads)
    
    # Run the worker with proper arguments
    run_worker()


async def run_db_init():
    """
    Initialize the database
    """
    from src.db.session import init_db
    
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully.")


def run_db_migrate(args):
    """
    Run database migrations
    """
    import subprocess
    
    print(f"Running database migrations to revision {args.revision}...")
    result = subprocess.run(["alembic", "upgrade", args.revision], check=True)
    
    if result.returncode == 0:
        print("Database migration completed successfully.")
    else:
        print("Database migration failed.")
        sys.exit(1)


def run_scheduler(args):
    """
    Run the task scheduler
    """
    import os
    from src.schedulers.scheduler_runner import main
    
    # Override scheduler enabled setting if specified in args
    if args.scheduler_enabled is not None:
        os.environ["SCHEDULER_ENABLED"] = str(args.scheduler_enabled).lower()
    
    print("Starting task scheduler...")
    asyncio.run(main())


def main():
    """
    Main entry point
    """
    args = parse_args()
    
    if args.command == "api":
        run_api(args)
    elif args.command == "worker":
        run_worker(args)
    elif args.command == "scheduler":
        run_scheduler(args)
    elif args.command == "db":
        if args.db_command == "init":
            asyncio.run(run_db_init())
        elif args.db_command == "migrate":
            run_db_migrate(args)
        else:
            print("Unknown database command. Use --help for assistance.")
            sys.exit(1)
    else:
        print("Unknown command. Use --help for assistance.")
        sys.exit(1)


if __name__ == "__main__":
    main()
