"""
Background task definitions using Dramatiq
"""
import logging
import time
import uuid
from typing import Dict, List, Optional, Union

import dramatiq
from dramatiq.middleware import Middleware

from src.core.config import settings


logger = logging.getLogger(__name__)


@dramatiq.actor(
    queue_name="default",
    max_retries=3,
    time_limit=60000,  # 60 seconds
)
def process_item(
    item_id: str,
    options: Optional[Dict] = None,
) -> Dict:
    """
    Example background task that processes an item.
    
    Args:
        item_id: The ID of the item to process
        options: Optional processing options
    
    Returns:
        A dictionary with the processing results
    """
    logger.info(f"Processing item {item_id}")
    
    # Simulate some processing work
    time.sleep(2)
    
    # Example result
    result = {
        "item_id": item_id,
        "processed": True,
        "timestamp": time.time(),
    }
    
    if options:
        result["options_used"] = options
    
    logger.info(f"Finished processing item {item_id}")
    return result


@dramatiq.actor(
    queue_name="low_priority",
    max_retries=5,
    time_limit=300000,  # 5 minutes
)
def generate_report(
    report_type: str,
    filters: Optional[Dict] = None,
    user_id: Optional[str] = None,
) -> str:
    """
    Example long-running task that generates a report.
    
    Args:
        report_type: The type of report to generate
        filters: Optional filters to apply to the report
        user_id: Optional ID of the user requesting the report
    
    Returns:
        A string with the report ID or location
    """
    logger.info(f"Generating {report_type} report for user {user_id}")
    
    # Simulate a long task
    time.sleep(10)
    
    # Generate a unique report ID
    report_id = str(uuid.uuid4())
    
    logger.info(f"Finished generating report {report_id}")
    return f"report:{report_id}"


@dramatiq.actor(queue_name="emails")
def send_welcome_email(user_email: str, user_name: str) -> None:
    """Send welcome email to new users"""
    logger.info(f"Sending welcome email to {user_email}")
    # Email sending logic would go here
    time.sleep(1)
    logger.info(f"Sent welcome email to {user_email}")


@dramatiq.actor(queue_name="emails")
def send_notification_email(user_email: str, subject: str, content: str) -> None:
    """Send notification email to users"""
    logger.info(f"Sending notification email to {user_email}: {subject}")
    # Email sending logic would go here
    time.sleep(0.5)
    logger.info(f"Sent notification email to {user_email}")


# Example of setting up a task group with middleware
email_group = dramatiq.group([
    send_welcome_email,
    send_notification_email,
])


# Example of a task with message hooks - using middleware instead of direct hooks
@dramatiq.actor
def data_processing_pipeline(data_id: str) -> None:
    """Process data through a pipeline with hooks"""
    logger.info(f"Starting data pipeline for {data_id}")
    time.sleep(2)
    logger.info(f"Completed data pipeline for {data_id}")


# Define a custom middleware for hooks instead of using direct method decorators
class PipelineMiddleware(Middleware):
    """Custom middleware to handle pipeline hooks"""
    
    def before_process_message(self, broker, message):
        if message.actor_name == "data_processing_pipeline":
            logger.info(f"Before pipeline hook: {message.args}")
        return message
    
    def after_process_message(self, broker, message, *, result=None, exception=None):
        if message.actor_name == "data_processing_pipeline":
            if exception is None:
                logger.info(f"After pipeline hook: {message.args}, result: {result}")
            else:
                logger.error(f"Pipeline error: {message.args}, exception: {str(exception)}")


# Note: To use this middleware, register it with your broker in worker.py:
#
# broker.add_middleware(PipelineMiddleware())
#
# Or if you're using the default broker:
# dramatiq.get_broker().add_middleware(PipelineMiddleware())
