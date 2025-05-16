"""
File-based cache backend implementation
"""
import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiofiles
import aiofiles.os

from src.cache.backends.base import CacheBackend
from src.core.config import settings


logger = logging.getLogger(__name__)


class FileBackend(CacheBackend):
    """
    File-based cache backend implementation
    
    Stores cache entries as JSON files in a directory structure
    """
    
    def __init__(self):
        self._cache_dir = Path(settings.CACHE_FILE_PATH)
        self._lock = asyncio.Lock()
        
    async def init(self) -> None:
        """Initialize the file cache directory"""
        logger.info(f"Initializing file cache at {self._cache_dir}")
        os.makedirs(self._cache_dir, exist_ok=True)
    
    async def close(self) -> None:
        """Close the file cache backend"""
        # Nothing to do
        pass
    
    def _get_path_for_key(self, key: str) -> Path:
        """Convert a cache key to a file path"""
        # Create a file-system safe representation of the key
        safe_key = key.replace(':', '_').replace('/', '_')
        return self._cache_dir / f"{safe_key}.json"
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value from the file cache"""
        try:
            path = self._get_path_for_key(key)
            
            if not path.exists():
                return None
                
            # Check if file is expired
            async with self._lock:
                stats = await aiofiles.os.stat(path)
                metadata_path = Path(f"{path}.meta")
                
                # Check expiration if metadata exists
                if metadata_path.exists():
                    async with aiofiles.open(metadata_path, 'r') as f:
                        metadata = json.loads(await f.read())
                        expiry = metadata.get('expiry')
                        
                        if expiry and time.time() > expiry:
                            # Expired, delete files
                            await aiofiles.os.remove(path)
                            await aiofiles.os.remove(metadata_path)
                            return None
                
                # Read the cache file
                async with aiofiles.open(path, 'r') as f:
                    return await f.read()
        except Exception as e:
            logger.error(f"File cache GET error: {str(e)}")
            return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a value in the file cache"""
        try:
            path = self._get_path_for_key(key)
            
            async with self._lock:
                # Write the value to the cache file
                async with aiofiles.open(path, 'w') as f:
                    await f.write(value)
                
                # Write expiration metadata if provided
                if ex is not None:
                    metadata = {
                        'created': time.time(),
                        'expiry': time.time() + ex
                    }
                    
                    metadata_path = Path(f"{path}.meta")
                    async with aiofiles.open(metadata_path, 'w') as f:
                        await f.write(json.dumps(metadata))
                
                return True
        except Exception as e:
            logger.error(f"File cache SET error: {str(e)}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys from the file cache"""
        if not keys:
            return 0
            
        deleted = 0
        
        try:
            async with self._lock:
                for key in keys:
                    path = self._get_path_for_key(key)
                    metadata_path = Path(f"{path}.meta")
                    
                    # Delete the cache file if it exists
                    if path.exists():
                        await aiofiles.os.remove(path)
                        deleted += 1
                    
                    # Delete the metadata file if it exists    
                    if metadata_path.exists():
                        await aiofiles.os.remove(metadata_path)
                        
            return deleted
        except Exception as e:
            logger.error(f"File cache DELETE error: {str(e)}")
            return deleted
    
    async def scan(self, cursor: Any, match: str, count: int) -> tuple[Any, List[str]]:
        """Scan the file cache for keys matching a pattern"""
        try:
            import fnmatch
            
            # Convert Redis-style pattern to glob pattern
            glob_pattern = match.replace('*', '?*')
            
            # Use cursor as an offset
            cursor = int(cursor) if cursor and cursor != b"0" else 0
            
            # List files in cache directory
            files = list(self._cache_dir.glob("*.json"))
            files = [f for f in files if not f.name.endswith('.meta.json')]
            
            # Extract keys from filenames
            all_keys = [f.stem for f in files]
            
            # Filter keys by pattern
            filtered_keys = []
            for key in all_keys:
                # Convert back from filesystem format to cache key format
                original_key = key.replace('_', ':')
                if fnmatch.fnmatch(original_key, glob_pattern):
                    filtered_keys.append(original_key)
            
            # Apply pagination
            end_idx = min(cursor + count, len(filtered_keys))
            result_keys = filtered_keys[cursor:end_idx]
            
            # Calculate next cursor
            next_cursor = str(end_idx) if end_idx < len(filtered_keys) else "0"
            
            return next_cursor, result_keys
        except Exception as e:
            logger.error(f"File cache SCAN error: {str(e)}")
            return "0", []
    
    async def flush(self) -> bool:
        """Clear all cached data in the file cache"""
        try:
            import shutil
            
            async with self._lock:
                # Remove all files in the cache directory
                if self._cache_dir.exists():
                    for item in self._cache_dir.glob("*"):
                        if item.is_file():
                            os.remove(item)
                        elif item.is_dir():
                            shutil.rmtree(item)
                    
                # Recreate the cache directory
                os.makedirs(self._cache_dir, exist_ok=True)
                
            return True
        except Exception as e:
            logger.error(f"File cache FLUSH error: {str(e)}")
            return False
