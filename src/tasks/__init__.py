"""
Background tasks module initialization
"""

from src.tasks.jobs import (
    process_item,
    generate_report,
    send_welcome_email,
    send_notification_email,
    data_processing_pipeline,
)
