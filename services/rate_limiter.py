"""
Rate limiter setup.

Flask-Limiter is initialised here and imported by app.py so that all
blueprints can use the same limiter instance via `from services.rate_limiter
import limiter`.

Default limits are intentionally conservative — AI endpoints cost real money
per call. Adjust the constants below if you need looser or tighter limits.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# One shared Limiter instance.  The Flask app is attached in app.py via
# limiter.init_app(app).
limiter = Limiter(
    key_func=get_remote_address,
    # Global default: 200 requests / day, 50 / hour per IP.
    # Individual routes can override with @limiter.limit("...").
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",   # In-process storage — resets on restart.
)