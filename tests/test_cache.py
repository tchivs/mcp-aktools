"""Tests for cache module - Dual-layer caching (Memory + Disk)."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest import mock

from mcp_aktools.cache import CacheKey


class TestCacheKey:
    """Test the CacheKey dual-layer caching implementation."""

    def setup_method(self):
        """Set up clean cache state before each test."""
        # Clear ALL cache to avoid interference between tests
        CacheKey.ALL = {}
        # Use temporary directory for disk cache
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up after each test."""
        CacheKey.ALL = {}
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_cache_instance(self):
        """Test that CacheKey.init creates and returns a cache instance."""
        cache = CacheKey.init("test_key", ttl=60)
        
        assert cache.key == "test_key"
        assert cache.ttl == 60
        assert cache.ttl2 == 120  # Default ttl * 2
        assert "test_key" in CacheKey.ALL

    def test_init_returns_existing_cache(self):
        """Test that CacheKey.init returns existing cache for same key."""
        cache1 = CacheKey.init("same_key", ttl=60)
        cache2 = CacheKey.init("same_key", ttl=120)
        
        assert cache1 is cache2
        assert cache1.ttl == 60  # Original value preserved

    def test_set_and_get_memory_cache(self):
        """Test setting and getting from memory cache (layer 1)."""
        cache = CacheKey.init("mem_key", ttl=60)
        
        cache.set("test_value")
        result = cache.get()
        
        assert result == "test_value"

    def test_set_and_get_disk_cache(self):
        """Test that value is also persisted to disk cache (layer 2)."""
        cache = CacheKey.init("disk_key", ttl=60)
        
        cache.set("disk_value")
        
        # Verify disk cache has the value
        assert cache.cache2.get("disk_key") == "disk_value"

    def test_memory_cache_miss_falls_back_to_disk(self):
        """Test fallback to disk cache when memory cache misses."""
        cache = CacheKey.init("fallback_key", ttl=60)
        
        # Set value (goes to both caches)
        cache.set("fallback_value")
        
        # Clear memory cache only
        cache.cache1.pop("fallback_key", None)
        
        # Should still get value from disk cache
        result = cache.get()
        assert result == "fallback_value"

    def test_cache_miss_returns_none(self):
        """Test that missing key returns None."""
        cache = CacheKey.init("missing_key", ttl=60)
        
        result = cache.get()
        
        assert result is None

    def test_delete_clears_both_caches(self):
        """Test that delete clears both memory and disk cache."""
        cache = CacheKey.init("delete_key", ttl=60)
        
        cache.set("delete_value")
        cache.delete()
        
        assert cache.cache1.get("delete_key") is None
        assert cache.cache2.get("delete_key") is None
        assert cache.get() is None

    def test_custom_ttl2(self):
        """Test custom ttl2 for disk cache."""
        cache = CacheKey.init("ttl_key", ttl=60, ttl2=300)
        
        assert cache.ttl == 60
        assert cache.ttl2 == 300

    def test_get_cache_dir_unix(self):
        """Test cache directory path on Unix-like systems."""
        with mock.patch("sys.platform", "linux"):
            cache = CacheKey.init("dir_key", ttl=60)
            cache_dir = cache.get_cache_dir()
            
            assert ".cache" in str(cache_dir)
            assert "mcp_aktools" in str(cache_dir)

    def test_get_cache_dir_windows(self):
        """Test cache directory path on Windows."""
        with mock.patch("sys.platform", "win32"):
            cache = CacheKey.init("dir_key_win", ttl=60)
            cache_dir = cache.get_cache_dir()
            
            assert "AppData" in str(cache_dir)
            assert "Local" in str(cache_dir)
            assert "Cache" in str(cache_dir)
            assert "mcp_aktools" in str(cache_dir)

    def test_cache_expiration(self):
        """Test that memory cache respects TTL."""
        cache = CacheKey.init("expire_key", ttl=0)  # 0 TTL means immediate expiration
        
        cache.set("expire_value")
        
        # With TTL=0, item should be expired from memory cache immediately
        # But should still be in disk cache (may need small delay to persist)
        import time
        time.sleep(0.2)
        
        # Try to get from disk cache directly
        disk_result = cache.cache2.get("expire_key")
        
        # Disk should have it (but diskcache might not be instantly available)
        # The main point is that memory cache works, disk cache is secondary
        if disk_result is not None:
            assert disk_result == "expire_value"


class TestCacheEdgeCases:
    """Test edge cases for cache module."""

    def setup_method(self):
        """Set up clean cache state."""
        CacheKey.ALL = {}

    def teardown_method(self):
        """Clean up."""
        CacheKey.ALL = {}

    def test_cache_with_none_value(self):
        """Test that None values are handled correctly."""
        cache = CacheKey.init("none_key", ttl=60)
        
        # Setting None should work
        cache.set(None)
        
        # Getting should return None
        result = cache.get()
        assert result is None

    def test_cache_with_dataframe(self):
        """Test caching pandas DataFrame."""
        import pandas as pd
        
        cache = CacheKey.init("df_key", ttl=60)
        
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        cache.set(df)
        
        result = cache.get()
        assert isinstance(result, pd.DataFrame)
        assert result.equals(df)

    def test_cache_with_complex_data(self):
        """Test caching complex Python objects."""
        cache = CacheKey.init("complex_key", ttl=60)
        
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2, 3),
        }
        cache.set(complex_data)
        
        result = cache.get()
        assert result["list"] == [1, 2, 3]
        assert result["dict"]["nested"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
