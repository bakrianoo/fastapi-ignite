"""
Scheduler configuration for periodic tasks
"""
import logging
from typing import Dict, List

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis

from src.core.config import settings


logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: AsyncIOScheduler = None


async def init_scheduler() -> AsyncIOScheduler:
    """
    Initialize and start the scheduler
    """
    global _scheduler
    
    if _scheduler and _scheduler.running:
        logger.warning("Scheduler is already running")
        return _scheduler
    
    logger.info("Initializing task scheduler")
    
    # Configure job stores
    jobstores = {
        'default': RedisJobStore(
            jobs_key='rankyx_ai_engine:scheduler:jobs',
            run_times_key='rankyx_ai_engine:scheduler:run_times',
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
    }
    
    # Configure executors
    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }
    
    # Create scheduler
    _scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults={
            'coalesce': True,         # Combine multiple pending executions
            'max_instances': 3,       # Maximum number of concurrent instances
            'misfire_grace_time': 60, # Seconds after the designated run time that the job is still allowed to be run
        }
    )
    
    # Set up scheduled jobs
    from src.schedulers.jobs import setup_jobs
    setup_jobs(_scheduler)
    
    # Start the scheduler
    _scheduler.start()
    logger.info("Task scheduler started")
    
    return _scheduler


async def shutdown_scheduler() -> None:
    """
    Shutdown the scheduler
    """
    global _scheduler
    
    if _scheduler and _scheduler.running:
        logger.info("Shutting down task scheduler")
        _scheduler.shutdown()
        _scheduler = None
    else:
        logger.warning("Scheduler is not running")


def get_scheduler() -> AsyncIOScheduler:
    """
    Get the scheduler instance
    """
    global _scheduler
    if not _scheduler:
        raise RuntimeError("Scheduler not initialized")
    return _scheduler


def get_scheduled_jobs() -> List[Dict]:
    """
    Get a list of all scheduled jobs
    """
    scheduler = get_scheduler()
    jobs = []
    
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'func': str(job.func),
            'next_run': str(job.next_run_time),
            'trigger': str(job.trigger),
        })
        
    return jobs
