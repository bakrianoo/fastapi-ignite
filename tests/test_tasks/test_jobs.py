"""
Tests for background tasks
"""
import pytest
from unittest.mock import patch

from src.tasks.jobs import process_item


@patch("src.tasks.jobs.logger")
def test_process_item(mock_logger):
    """
    Test the process_item background task
    """
    # Execute task function directly (not as a Dramatiq actor)
    item_id = "test-item-123"
    options = {"priority": "high"}
    
    result = process_item(item_id, options)
    
    # Verify result
    assert result["item_id"] == item_id
    assert result["processed"] == True
    assert "timestamp" in result
    assert result["options_used"] == options
    
    # Verify logging
    mock_logger.info.assert_any_call(f"Processing item {item_id}")
    mock_logger.info.assert_any_call(f"Finished processing item {item_id}")


@patch("src.tasks.jobs.time.sleep")
@patch("src.tasks.jobs.logger")
def test_process_item_timing(mock_logger, mock_sleep):
    """
    Test that the process_item task uses sleep as expected
    """
    # Mock sleep to avoid waiting
    mock_sleep.return_value = None
    
    # Execute task
    process_item("test-id")
    
    # Verify sleep was called
    mock_sleep.assert_called_once_with(2)


@pytest.mark.parametrize("item_id,options", [
    ("item-1", {"flag": True}),
    ("item-2", None),
    ("item-3", {"priority": "low", "retry": False}),
])
def test_process_item_parameters(item_id, options):
    """
    Test process_item with different parameters
    """
    result = process_item(item_id, options)
    
    assert result["item_id"] == item_id
    assert result["processed"] == True
    
    if options:
        assert result["options_used"] == options
    else:
        assert "options_used" not in result
