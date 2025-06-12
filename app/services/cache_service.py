from cachetools import TTLCache
from app.core.config import CACHE_TTL, CACHE_MAXSIZE

# Create cache instances
carpark_ids_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
carpark_locations_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
no_update_carparks_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)
