"""
Tests for caching functionality
"""
import pytest
import redis.asyncio as redis
from unittest import mock

from src.cache.decorators import cached
from src.cache.redis import init_redis_pool


@pytest.mark.asyncio
async def test_cached_decorator():
    """
    Test the cached decorator functionality
    """
    # Mock Redis get and set methods
    mock_redis = mock.AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    
    # Create a function with the cached decorator
    call_count = 0
    
    @cached(ttl=60, key_prefix="test")
    async def test_function(a: int, b: str) -> dict:
        nonlocal call_count
        call_count += 1
        return {"a": a, "b": b}
    
    # Call function first time (should miss cache)
    result1 = await test_function(1, "test", redis=mock_redis)
    assert result1 == {"a": 1, "b": "test"}
    assert call_count == 1
    
    # Redis get should have been called, but returned None
    mock_redis.get.assert_called_once()
    
    # Redis set should have been called once
    mock_redis.set.assert_called_once()
    
    # Reset mocks for next call
    mock_redis.reset_mock()
    
    # Set up mock to return a cached result
    mock_redis.get.return_value = '{"a": 1, "b": "test"}'
    
    # Call function second time with same args (should hit cache)
    result2 = await test_function(1, "test", redis=mock_redis)
    assert result2 == {"a": 1, "b": "test"}
    
    # Function should not have been called again
    assert call_count == 1
    
    # Redis get should have been called
    mock_redis.get.assert_called_once()
    
    # Redis set should not have been called
    mock_redis.set.assert_not_called()
    
    # Reset mocks for next call
    mock_redis.reset_mock()
    
    # Call function with different args (should miss cache)
    mock_redis.get.return_value = None
    result3 = await test_function(2, "test", redis=mock_redis)
    assert result3 == {"a": 2, "b": "test"}
    
    # Function should have been called again
    assert call_count == 2
    
    # Redis get and set should have been called
    mock_redis.get.assert_called_once()
    mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_cache_key_builder():
    """
    Test custom key builder for cached decorator
    """
    # Mock Redis
    mock_redis = mock.AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    
    # Custom key builder function
    def custom_key_builder(*args, **kwargs) -> str:
        user_id = kwargs.get("user_id", "unknown")
        action = kwargs.get("action", "default")
        return f"custom:{user_id}:{action}"
    
    # Create a function with the cached decorator and custom key builder
    call_count = 0
    
    @cached(ttl=60, key_builder=custom_key_builder)
    async def test_function(user_id: str, action: str) -> dict:
        nonlocal call_count
        call_count += 1
        return {"user_id": user_id, "action": action}
    
    # Call function
    result = await test_function(user_id="123", action="test", redis=mock_redis)
    assert result == {"user_id": "123", "action": "test"}
    assert call_count == 1
    
    # The key should have been built using the custom key builder
    mock_redis.get.assert_called_once()
    args, kwargs = mock_redis.get.call_args
    assert args[0] == "custom:123:test"
