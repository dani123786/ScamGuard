"""Authentication and authorization module for the admin interface."""

import os
import secrets
import functools
from datetime import datetime, timedelta

from flask import session, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

# Session timeout in minutes
SESSION_TIMEOUT_MINUTES = 30

# Dev fallback is ONLY used when this env var is explicitly set to '1'.
# Setting FLASK_ENV=development is NOT sufficient — this prevents the
# backdoor from activating on a misconfigured production deployment.
_DEV_FALLBACK_ENABLED = os.environ.get('SCAMGUARD_DEV_FALLBACK') == '1'

_DEV_USER = {
    'id': 0,
    'username': 'admin',
    'password_hash': generate_password_hash('admin123', method='pbkdf2:sha256'),
    'role': 'admin',
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log_auth_event(event_type: str, username: str, success: bool, details: str = None):
    """Print a structured authentication log line.

    event_type: 'LOGIN' | 'LOGOUT' | 'AUTH_FAILURE' | 'AUTHZ_FAILURE'
    """
    ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    status = 'SUCCESS' if success else 'FAILURE'
    msg = f"[AUTH] {ts} event={event_type} user={username} status={status}"
    if details:
        msg += f" details={details}"
    print(msg)

# ---------------------------------------------------------------------------
# Core auth helpers
# ---------------------------------------------------------------------------

def login_user(username: str, password: str, supabase_client=None):
    """Validate credentials against admin_users table (or dev fallback).

    Returns a user dict on success, None on failure.

    The dev fallback (admin/admin123) is only active when the environment
    variable SCAMGUARD_DEV_FALLBACK=1 is explicitly set. It is never active
    in an unmodified production deployment.
    """
    if supabase_client is not None:
        try:
            result = supabase_client.table('admin_users').select('*').eq('username', username).execute()
            if result.data:
                user = result.data[0]
                if check_password_hash(user.get('password_hash', ''), password):
                    log_auth_event('LOGIN', username, True)
                    return {
                        'id': user.get('id'),
                        'username': user.get('username'),
                        'role': user.get('role', 'viewer'),
                    }
                log_auth_event('LOGIN', username, False, 'bad password')
                return None
            # User not found in DB — fall through to dev fallback if enabled
        except Exception as e:
            print(f"[AUTH] DB error during login: {e}")
            # Fall through to dev fallback only if explicitly enabled

    # Dev fallback — requires SCAMGUARD_DEV_FALLBACK=1 in environment
    if _DEV_FALLBACK_ENABLED:
        if username == _DEV_USER['username'] and check_password_hash(_DEV_USER['password_hash'], password):
            log_auth_event('LOGIN', username, True, 'dev-fallback')
            return {'id': _DEV_USER['id'], 'username': _DEV_USER['username'], 'role': _DEV_USER['role']}

    log_auth_event('LOGIN', username, False, 'user not found or DB unavailable')
    return None


def get_current_user(sess=None):
    """Return the current user dict from session, or None if not authenticated / timed out."""
    if sess is None:
        sess = session

    user_id = sess.get('user_id')
    if user_id is None:
        return None

    login_time = sess.get('login_time')
    if login_time is None:
        return None

    # Parse login_time (stored as ISO string)
    try:
        if isinstance(login_time, str):
            login_dt = datetime.fromisoformat(login_time)
        else:
            login_dt = login_time
    except (ValueError, TypeError):
        _clear_session(sess)
        return None

    # Check timeout
    if datetime.utcnow() - login_dt > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        _clear_session(sess)
        return None

    return {
        'id': user_id,
        'username': sess.get('username'),
        'role': sess.get('role'),
    }


def _clear_session(sess=None):
    if sess is None:
        sess = session
    for key in ('user_id', 'username', 'role', 'login_time', 'csrf_token'):
        sess.pop(key, None)

# ---------------------------------------------------------------------------
# CSRF
# ---------------------------------------------------------------------------

def generate_csrf_token() -> str:
    """Generate a random CSRF token and store it in the session."""
    token = secrets.token_hex(32)
    session['csrf_token'] = token
    return token


def validate_csrf_token(req=None) -> bool:
    """Check that the CSRF token in the request matches the session token.

    Checks JSON body key 'csrf_token' and header 'X-CSRF-Token'.
    """
    if req is None:
        req = request

    session_token = session.get('csrf_token')
    if not session_token:
        return False

    # Check header first
    header_token = req.headers.get('X-CSRF-Token')
    if header_token and secrets.compare_digest(header_token, session_token):
        return True

    # Check JSON body
    try:
        body = req.get_json(silent=True) or {}
        body_token = body.get('csrf_token', '')
        if body_token and secrets.compare_digest(body_token, session_token):
            return True
    except Exception:
        pass

    return False

# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def require_auth(f):
    """Decorator: require a valid authenticated session.
    Browser requests are redirected to /admin/login.
    API requests (JSON) get a 401 response.
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            log_auth_event('AUTH_FAILURE', 'anonymous', False, f'unauthenticated access to {request.path}')
            if request.accept_mimetypes.accept_html and not request.is_json:
                return redirect('/admin/login')
            return jsonify({'error': 'Authentication required', 'authenticated': False}), 401
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Decorator factory: require the current user's role to be in *roles, else return 403."""
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if user is None:
                log_auth_event('AUTH_FAILURE', 'anonymous', False, f'unauthenticated access to {request.path}')
                if request.accept_mimetypes.accept_html and not request.is_json:
                    return redirect('/admin/login')
                return jsonify({'error': 'Authentication required', 'authenticated': False}), 401
            if user.get('role') not in roles:
                log_auth_event('AUTHZ_FAILURE', user.get('username', ''), False,
                               f"role={user.get('role')} required={roles} path={request.path}")
                return jsonify({'error': 'Insufficient permissions', 'required_roles': list(roles)}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
