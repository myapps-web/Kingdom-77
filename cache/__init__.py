"""
Cache Package for Kingdom-77 Bot v3.0
======================================
Provides caching layer with Redis support.
"""

from .redis import RedisCache, cache, init_cache, close_cache

__all__ = ['RedisCache', 'cache', 'init_cache', 'close_cache']
__version__ = '3.0.0'
