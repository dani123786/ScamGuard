"""
ScamGuard AI — Flask application entry point.

Responsibilities:
  1. Load environment variables
  2. Create the Flask app
  3. Initialise all shared objects in routes/extensions.py
  4. Register all blueprints
"""
import os
import warnings
from dotenv import load_dotenv
load_dotenv()

from flask import Flask

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Secret key — MUST be set via environment variable in production
# ---------------------------------------------------------------------------
_secret = os.environ.get('SECRET_KEY')
if not _secret:
    _secret = 'scamguard-default-secret-2026'
    warnings.warn(
        "[SECURITY] SECRET_KEY is not set in environment variables. "
        "Using the hardcoded default — this is UNSAFE in production. "
        "Set SECRET_KEY in your .env or deployment config.",
        stacklevel=1
    )
app.secret_key = _secret

# ---------------------------------------------------------------------------
# FIX: Production session cookie settings for Vercel (HTTPS)
# Without these, admin sessions won't persist correctly on Vercel because:
#   - SESSION_COOKIE_SECURE=True ensures cookies are sent only over HTTPS
#   - SESSION_COOKIE_HTTPONLY=True prevents JS from reading the cookie (security)
#   - SESSION_COOKIE_SAMESITE='Lax' prevents CSRF while allowing normal navigation
# ---------------------------------------------------------------------------
_is_production = (
    os.environ.get('FLASK_ENV') == 'production' or
    os.environ.get('VERCEL') == '1' or
    os.environ.get('VERCEL_ENV') in ('production', 'preview')
)

if _is_production:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    print("[+] Production session cookie settings applied (Secure, HttpOnly, SameSite=Lax)")
else:
    # Localhost — don't force HTTPS for cookies
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ---------------------------------------------------------------------------
# Rate limiter (must be init'd before blueprints are registered)
# ---------------------------------------------------------------------------
try:
    from services.rate_limiter import limiter
    limiter.init_app(app)
    print("[+] Rate limiter initialised")
except Exception as _rl_err:
    print(f"[!] Rate limiter init failed: {_rl_err}")

# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------
supabase_client = None
try:
    from supabase import create_client
    supabase_url = (
        os.environ.get('SUPABASE_URL') or
        os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or
        os.environ.get('SUPABASE_PROJECT_URL')
    )
    supabase_key = (
        os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or
        os.environ.get('SUPABASE_KEY') or
        os.environ.get('SUPABASE_ANON_KEY')
    )
    if supabase_url and supabase_key:
        try:
            supabase_client = create_client(supabase_url, supabase_key)
            key_name = (
                'SUPABASE_SERVICE_ROLE_KEY' if os.environ.get('SUPABASE_SERVICE_ROLE_KEY') else
                'SUPABASE_KEY' if os.environ.get('SUPABASE_KEY') else
                'SUPABASE_ANON_KEY'
            )
            print(f"[+] Supabase connected successfully using {key_name}")
        except Exception as e:
            print(f"[!] Supabase connection failed: {e}")
    else:
        print("[!] Supabase credentials not found in environment")
except ImportError:
    print("Warning: Supabase not installed. Reports will save locally only.")

# ---------------------------------------------------------------------------
# Shared objects — populate routes/extensions.py module-level vars
# ---------------------------------------------------------------------------
import routes.extensions as ext

from services.cache_manager import SimpleCacheManager
ext._cache_manager = SimpleCacheManager()

try:
    from services.content_service import ContentService
    ext.content_service = ContentService(supabase_client, ext._cache_manager)
    ext.content_service.fallback_enabled = False
    print("[+] ContentService initialised (database-only mode)")
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
# Register blueprints
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
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
