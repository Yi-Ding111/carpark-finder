import time
from collections import deque
from typing import Deque, Dict

from fastapi import Request
from fastapi.responses import JSONResponse


class SimpleRateLimiter:
    def __init__(self, requests_per_second: int = 5):
        """
        Initialize the rate limiter.

        Parameters:
            requests_per_second: The number of requests per second allowed for each API key.
        """
        self.requests_per_second = requests_per_second
        # Use a dictionary to store the request timestamps for each API key
        self.requests: Dict[str, Deque[float]] = {}

    def is_rate_limited(self, api_key: str) -> bool:
        """
        Check if the API key has exceeded the rate limit.

        Parameters:
            api_key: The API key to check.
        """
        current_time = time.time()

        # If the API key is not in the dictionary, initialize an empty queue
        if api_key not in self.requests:
            self.requests[api_key] = deque()

        # Clean up old requests that are more than 1 second old
        while self.requests[api_key] and current_time - self.requests[api_key][0] > 1:
            self.requests[api_key].popleft()

        # If the number of requests in the current second exceeds the limit, return True
        if len(self.requests[api_key]) >= self.requests_per_second:
            return True

        # Add the new request timestamp
        self.requests[api_key].append(current_time)
        return False


# Create a global rate limiter instance
rate_limiter = SimpleRateLimiter(requests_per_second=5)


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to rate limit requests.

    Parameters:
        request: The incoming request.
        call_next: The next middleware function to call.
    """
    # Skip rate limiting for documentation endpoints
    if request.url.path in {"/docs", "/openapi.json", "/redoc"}:
        return await call_next(request)

    # Get the API key from the request headers
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return await call_next(request)

    if rate_limiter.is_rate_limited(api_key):
        return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again in a second."})

    response = await call_next(request)
    return response
