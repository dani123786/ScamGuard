"""
ScamGuard AI — Flask application entry point.
Optimized for Render Deployment with Port & Host fixes.
Now with WhiteNoise for Static File serving.
"""
import os
import warnings
import logging
from dotenv import load_dotenv
from flask import Flask
from whitenoise import WhiteNoise  # <-- ADDED THIS

# 1. Load environment variables
load_dotenv()

# Setup basic logging for Render logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- WHITE NOISE CONFIGURATION (FIXES STYLING/CSS) ---
# This tells Render to serve files from your 'static' folder automatically.
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/') 

# ---------------------------------------------------------------------------
# Secret key — Set 'SECRET_KEY' in Render Dashboard for security
# ---------------------------------------------------------------------------
_secret = os.environ.get('SECRET_KEY')
if not _secret:
    _secret = 'scamguard-default-secret-2026'
    warnings.warn(
        "[SECURITY] SECRET_KEY is not set. Using default — UNSAFE for production.",
        stacklevel=1
    )
app.secret_key = _secret

# ---------------------------------------------------------------------------
# Production Check: Detects if running on Render
# ---------------------------------------------------------------------------
_is_production = (
    os.environ.get('FLASK_ENV') == 'production' or
    os.environ.get('RENDER') == 'true'
)

if _is_production:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    print("[+] Production mode: Secure session cookies enabled.")
else:
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['DEBUG'] = True
    print("[!] Development mode: Debugging active.")

# ---------------------------------------------------------------------------
# Google GenAI Safety Check
# ---------------------------------------------------------------------------
try:
    from google import genai
    print("[+] Google GenAI module loaded")
except ImportError:
    print("[!] WARNING: google-genai package not installed. Check requirements.txt")

# ---------------------------------------------------------------------------
# Rate limiter initialization
# ---------------------------------------------------------------------------
try:
    from services.rate_limiter import limiter
    limiter.init_app(app)
    print("[+] Rate limiter initialised")
except Exception as _rl_err:
    print(f"[!] Rate limiter init failed: {_rl_err}")

# ---------------------------------------------------------------------------
# Supabase Connection
# ---------------------------------------------------------------------------
supabase_client = None
try:
    from supabase import create_client
    supabase_url = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        try:
            supabase_client = create_client(supabase_url, supabase_key)
            print("[+] Supabase connected successfully")
        except Exception as e:
            print(f"[!] Supabase connection failed: {e}")
    else:
        print("[!] Supabase credentials missing from environment variables")
except ImportError:
    print("[!] Warning: Supabase library not found in requirements.txt")

# ---------------------------------------------------------------------------
# Shared objects — Register with routes/extensions.py
# ---------------------------------------------------------------------------
import routes.extensions as ext
from services.cache_manager import SimpleCacheManager
ext._cache_manager = SimpleCacheManager()

try:
    from services.content_service import ContentService
    ext.content_service = ContentService(supabase_client, ext._cache_manager)
    ext.content_service.fallback_enabled = False
    print("[+] ContentService initialised")
except Exception as _e:
    ext.content_service = None
    print(f"[!] ContentService init failed: {_e}")

try:
    from services.content_validator import ContentValidator
    ext._content_validator = ContentValidator()
except Exception as _cv_err:
    ext._content_validator = None
    print(f"[!] ContentValidator init failed: {_cv_err}")

try:
    from services.audit_logger import AuditLogger
    ext._audit_logger = AuditLogger(supabase_client, changed_by='admin')
except Exception as _al_err:
    ext._audit_logger = None
    print(f"[!] AuditLogger init failed: {_al_err}")

ext.supabase_client = supabase_client

try:
    from services.auth import (
        login_user as _auth_login_user,
        get_current_user as _auth_get_current_user,
        generate_csrf_token as _auth_generate_csrf_token,
        validate_csrf_token as _auth_validate_csrf_token,
        log_auth_event as _auth_log_auth_event,
        require_auth,
        require_role,
        _clear_session as _auth_clear_session,
    )
    ext._AUTH_AVAILABLE = True
    ext.require_auth = require_auth
    ext.require_role = require_role
    ext._auth_login_user = _auth_login_user
    ext._auth_get_current_user = _auth_get_current_user
    ext._auth_generate_csrf_token = _auth_generate_csrf_token
    ext._auth_validate_csrf_token = _auth_validate_csrf_token
    ext._auth_log_auth_event = _auth_log_auth_event
    ext._auth_clear_session = _auth_clear_session
    print("[+] Auth module loaded")
except Exception as _auth_err:
    ext._AUTH_AVAILABLE = False
    print(f"[!] Auth module init failed: {_auth_err}")

# ---------------------------------------------------------------------------
# Register Blueprints
# ---------------------------------------------------------------------------
from routes.public import public
from routes.api import api
from routes.auth_routes import auth
from routes.admin_routes import admin_content
from routes.analytics_routes import analytics

app.register_blueprint(public)
app.register_blueprint(api)
app.register_blueprint(auth)
app.register_blueprint(admin_content)
app.register_blueprint(analytics)

# ---------------------------------------------------------------------------
# Execution Entry Point (Optimized for Render)
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"--- ScamGuard AI Process Initializing ---")
    print(f"[+] Targeting Port: {port}")
    print(f"[+] Environment: {'Production' if _is_production else 'Development'}")
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=not _is_production)
