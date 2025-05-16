"""
Tests for the cache backends
"""
import pytest

from src.cache.backends.base import CacheBackend
from src.cache.backends.memory import MemoryBackend
from src.cache.backends.file import FileBackend
from src.cache.backends.redis import RedisBackend


@pytest.mark.asyncio
class TestCacheBackends:
    """Tests for different cache backend implementations"""

    async def test_memory_backend_basic_ops(self):
        """Test basic operations with memory backend"""
        cache = MemoryBackend()
        await cache.init()
        
        try:
            # Set a value
            await cache.set("test_key", "test_value")
            
            # Get the value
            value = await cache.get("test_key")
            assert value == "test_value"
            
            # Delete the value
            deleted = await cache.delete("test_key")
            assert deleted == 1
            
            # Confirm it's gone
            value = await cache.get("test_key")
            assert value is None
        finally:
            await cache.close()

    @pytest.mark.asyncio
    async def test_memory_backend_expiry(self):
        """Test expiration with memory backend"""
        cache = MemoryBackend()
        await cache.init()
        
        try:
            # Set with a very short TTL (1 second)
            await cache.set("expiry_test", "value", ex=1)
            
            # Should be available immediately
            value = await cache.get("expiry_test")
            assert value == "value"
            
            # Wait for expiration
            import asyncio
            await asyncio.sleep(1.1)
            
            # Should be gone now
            value = await cache.get("expiry_test")
            assert value is None
        finally:
            await cache.close()

    @pytest.mark.asyncio
    async def test_memory_backend_scan(self):
        """Test scan operation with memory backend"""
        cache = MemoryBackend()
        await cache.init()
        
        try:
            # Set multiple values with different prefixes
            await cache.set("user:1", "user1")
            await cache.set("user:2", "user2")
            await cache.set("item:1", "item1")
            
            # Scan for user keys
            cursor, keys = await cache.scan("0", "user:*", 10)
            assert len(keys) == 2
            assert "user:1" in keys
            assert "user:2" in keys
            
            # Scan for item keys
            cursor, keys = await cache.scan("0", "item:*", 10)
            assert len(keys) == 1
            assert "item:1" in keys
            
            # Clean up
            await cache.flush()
        finally:
            await cache.close()
            
    @pytest.mark.asyncio
    async def test_file_backend_basic_ops(self):
        """Test basic operations with file backend"""
        import tempfile
        import os
        from pathlib import Path
        
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Override the cache path
            from src.core.config import settings
            original_path = settings.CACHE_FILE_PATH
            settings.cache.file_path = temp_dir
            
            cache = FileBackend()
            await cache.init()
            
            try:
                # Set a value
                await cache.set("test_key", "test_value")
                
                # Verify file was created
                file_path = cache._get_path_for_key("test_key")
                assert file_path.exists()
                
                # Get the value
                value = await cache.get("test_key")
                assert value == "test_value"
                
                # Delete the value
                deleted = await cache.delete("test_key")
                assert deleted == 1
                assert not file_path.exists()
                
                # Confirm it's gone
                value = await cache.get("test_key")
                assert value is None
            finally:
                await cache.close()
                # Restore original path
                settings.cache.file_path = original_path
