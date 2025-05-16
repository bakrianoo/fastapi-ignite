"""
Dramatiq worker configuration
"""
import logging
import os
import sys

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, Callbacks, Pipelines, Retries, TimeLimit

from src.core.config import settings


logger = logging.getLogger(__name__)

# Configure Redis broker for Dramatiq
redis_broker = RedisBroker(
    url=str(settings.REDIS_URI),
    middleware=[
        Pipelines(),
        Retries(max_retries=3),
        TimeLimit(),
        AgeLimit(),
        Callbacks(),
    ]
)

# Set as the default broker
dramatiq.set_broker(redis_broker)

# Function to run the worker (used in CLI scripts)
def run_worker() -> None:
    """
    Run the Dramatiq worker
    """
    from dramatiq.cli import main
    
    # Set up arguments for the worker
    os.environ["PYTHONPATH"] = os.getcwd()
    sys.argv = [
        "dramatiq",
        "src.tasks.jobs",  # Import path for task modules
        "-p", str(settings.DRAMATIQ_PROCESSES),  # Number of processes
        "-t", str(settings.DRAMATIQ_THREADS),    # Number of threads per process
    ]
    
    logger.info("Starting Dramatiq worker")
    main()
