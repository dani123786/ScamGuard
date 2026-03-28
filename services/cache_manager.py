"""Simple in-memory cache with TTL support."""
import time

class SimpleCacheManager:
    """Minimal in-memory cache with TTL support."""

    def __init__(self):
        self._store = {}  # key -> (value, expires_at)

    def get(self, key):
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at is not None and time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key, value, timeout=3600):
        expires_at = time.time() + timeout if timeout else None
        self._store[key] = (value, expires_at)

    def delete(self, key):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()
