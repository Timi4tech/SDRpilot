
import os

TESTING = os.getenv("ENV") == "test"
from .auth_middleware import AuthMiddleware
#from .logging import LoggingMiddleware
#from .cache_middleware import cache_response
from .ratelimit_middleware import RateLimiterMiddleware



def setup_middleware(app):
    if TESTING:
        return  # skip middleware in tests
    app.add_middleware(RateLimiterMiddleware)
    app.add_middleware(AuthMiddleware, protected_prefix="/protected")
    #app.add_middleware(LoggingMiddleware)
    #app.add_middleware(cache_response)
    