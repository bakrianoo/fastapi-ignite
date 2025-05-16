"""
Runner script for the APScheduler scheduler
"""
import asyncio
import logging
import os
import signal
import sys
from typing import Set

from src.core.config import settings
from src.core.logging import setup_logging
from src.schedulers.scheduler import init_scheduler, shutdown_scheduler


logger = logging.getLogger(__name__)

# Global signal handling
shutdown_signal_received = False
signals_to_handle = {signal.SIGINT, signal.SIGTERM}
original_handlers: dict = {}


def handle_signal(sig, frame):
    """
    Signal handler for graceful shutdown
    """
    global shutdown_signal_received
    logger.info(f"Received signal {sig}, shutting down...")
    shutdown_signal_received = True
    
    # Restore original signal handlers
    for sig in signals_to_handle:
        if sig in original_handlers:
            signal.signal(sig, original_handlers[sig])


def setup_signal_handlers():
    """
    Set up signal handlers for graceful shutdown
    """
    global original_handlers
    
    for sig in signals_to_handle:
        original_handlers[sig] = signal.getsignal(sig)
        signal.signal(sig, handle_signal)


def is_scheduler_enabled() -> bool:
    """
    Check if the scheduler is enabled based on environment variable or settings
    """
    # Check environment variable first (set by CLI)
    env_enabled = os.environ.get("SCHEDULER_ENABLED")
    if env_enabled is not None:
        return env_enabled.lower() == "true"
    
    # Fall back to settings
    return settings.SCHEDULER_ENABLED


async def main():
    """
    Main entry point for the scheduler runner
    """
    # Set up logging
    setup_logging()
    
    # Check if scheduler is enabled
    if not is_scheduler_enabled():
        logger.info("Scheduler is disabled. Exiting.")
        return
    
    # Initialize the scheduler
    scheduler = await init_scheduler()
    
    logger.info(f"Scheduler runner started in {settings.ENV} mode")
    
    # Wait until a shutdown signal is received
    while not shutdown_signal_received:
        await asyncio.sleep(1)
    
    # Shutdown the scheduler
    await shutdown_scheduler()
    logger.info("Scheduler runner shutdown complete")


if __name__ == "__main__":
    # Setup signal handlers
    setup_signal_handlers()
    
    try:
        # Run the main coroutine
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Unhandled exception in scheduler runner: {str(e)}")
        sys.exit(1)
