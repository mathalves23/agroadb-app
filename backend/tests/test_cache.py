"""
Tests for Cache Service
"""
import pytest
import asyncio
from app.core.cache import CacheService


class TestCacheService:
    """Test cache service functionality"""
    
    @pytest.fixture
    async def cache_service(self):
        """Create cache service instance"""
        service = CacheService()
        await service.connect()
        yield service
        await service.disconnect()
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_service: CacheService):
        """Test setting and getting cache values"""
        key = "test_key"
        value = {"data": "test_value"}
        
        await cache_service.set(key, value)
        result = await cache_service.get(key)
        
        assert result == value
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_service: CacheService):
        """Test getting nonexistent key"""
        result = await cache_service.get("nonexistent_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete(self, cache_service: CacheService):
        """Test deleting cache key"""
        key = "test_delete"
        value = "test_value"
        
        await cache_service.set(key, value)
        await cache_service.delete(key)
        result = await cache_service.get(key)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache_service: CacheService):
        """Test TTL expiration"""
        key = "test_ttl"
        value = "test_value"
        ttl = 1  # 1 second
        
        await cache_service.set(key, value, ttl=ttl)
        
        # Value should exist immediately
        result = await cache_service.get(key)
        assert result == value
        
        # Wait for expiration
        await asyncio.sleep(2)
        
        # Value should be expired
        result = await cache_service.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_pattern_deletion(self, cache_service: CacheService):
        """Test deleting keys by pattern"""
        # Set multiple keys with pattern
        await cache_service.set("user:1:profile", {"name": "User 1"})
        await cache_service.set("user:2:profile", {"name": "User 2"})
        await cache_service.set("user:1:settings", {"theme": "dark"})
        await cache_service.set("other:key", {"data": "other"})
        
        # Delete all user:* keys
        await cache_service.delete_pattern("user:*")
        
        # User keys should be deleted
        assert await cache_service.get("user:1:profile") is None
        assert await cache_service.get("user:2:profile") is None
        assert await cache_service.get("user:1:settings") is None
        
        # Other key should still exist
        assert await cache_service.get("other:key") is not None
    
    @pytest.mark.asyncio
    async def test_increment(self, cache_service: CacheService):
        """Test incrementing numeric values"""
        key = "counter"
        
        # Set initial value
        await cache_service.set(key, 0)
        
        # Increment
        result = await cache_service.increment(key)
        assert result == 1
        
        # Increment again
        result = await cache_service.increment(key, 5)
        assert result == 6
    
    @pytest.mark.asyncio
    async def test_exists(self, cache_service: CacheService):
        """Test checking if key exists"""
        key = "test_exists"
        
        # Key doesn't exist
        assert await cache_service.exists(key) is False
        
        # Set key
        await cache_service.set(key, "value")
        
        # Key exists
        assert await cache_service.exists(key) is True
    
    @pytest.mark.asyncio
    async def test_cache_complex_objects(self, cache_service: CacheService):
        """Test caching complex objects"""
        complex_data = {
            "id": 1,
            "name": "Test",
            "nested": {
                "list": [1, 2, 3],
                "dict": {"key": "value"}
            },
            "boolean": True,
            "null": None
        }
        
        key = "complex_object"
        await cache_service.set(key, complex_data)
        result = await cache_service.get(key)
        
        assert result == complex_data
    
    @pytest.mark.asyncio
    async def test_cache_list_operations(self, cache_service: CacheService):
        """Test list operations in cache"""
        key = "test_list"
        
        # Push items to list
        await cache_service.lpush(key, "item1")
        await cache_service.lpush(key, "item2")
        await cache_service.lpush(key, "item3")
        
        # Get list length
        length = await cache_service.llen(key)
        assert length == 3
        
        # Get range
        items = await cache_service.lrange(key, 0, -1)
        assert len(items) == 3
    
    @pytest.mark.asyncio
    async def test_cache_decorator(self, cache_service: CacheService):
        """Test cache decorator functionality"""
        call_count = 0
        
        @cache_service.cached(ttl=60)
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute function
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
        
        # Different argument - should execute function
        result3 = await expensive_function(10)
        assert result3 == 20
        assert call_count == 2


class TestCachePerformance:
    """Test cache performance"""
    
    @pytest.mark.asyncio
    async def test_bulk_set_performance(self, cache_service: CacheService):
        """Test bulk setting performance"""
        import time
        
        start = time.time()
        
        # Set 100 items
        for i in range(100):
            await cache_service.set(f"perf_test:{i}", {"value": i})
        
        end = time.time()
        duration = end - start
        
        # Should complete in reasonable time (< 1 second for 100 items)
        assert duration < 1.0
    
    @pytest.mark.asyncio
    async def test_bulk_get_performance(self, cache_service: CacheService):
        """Test bulk getting performance"""
        import time
        
        # Set 100 items
        for i in range(100):
            await cache_service.set(f"perf_test:{i}", {"value": i})
        
        start = time.time()
        
        # Get 100 items
        for i in range(100):
            await cache_service.get(f"perf_test:{i}")
        
        end = time.time()
        duration = end - start
        
        # Should complete in reasonable time
        assert duration < 1.0
