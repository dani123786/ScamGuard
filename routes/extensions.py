"""
Shared application objects for all blueprints.

app.py initialises these after creating the Flask app, then each blueprint
imports from here to avoid circular imports.
"""

# These are set by app.py at startup
supabase_client = None
_cache_manager = None
content_service = None
_content_validator = None
_audit_logger = None
_AUTH_AVAILABLE = False

# ---------------------------------------------------------------------------
# Auth stubs — replaced by real implementations when auth module loads.
#
# IMPORTANT: The stubs for require_auth and require_role deliberately raise
# RuntimeError instead of silently passing through. This means if the auth
# module fails to import, ALL protected routes return a 500 error rather than
# silently allowing unauthenticated access.
# ---------------------------------------------------------------------------

def _auth_not_available_error():
    raise RuntimeError(
        "[SECURITY] Auth module failed to load. All protected routes are "
        "disabled. Check startup logs for the import error."
    )

def require_auth(f):
    import functools
    @functools.wraps(f)
    def protected(*args, **kwargs):
        _auth_not_available_error()
    return protected

def require_role(*roles):
    def decorator(f):
        import functools
        @functools.wraps(f)
        def protected(*args, **kwargs):
            _auth_not_available_error()
        return protected
    return decorator

def _auth_login_user(username, password, client):
    return None

def _auth_get_current_user():
    return None

def _auth_generate_csrf_token():
    return 'csrf-unavailable'

def _auth_validate_csrf_token():
    return False

def _auth_log_auth_event(event_type, username, success, details=None):
    pass

def _auth_clear_session():
    from flask import session
    session.clear()


# ---------------------------------------------------------------------------
# Cache invalidation helpers (used by multiple blueprints)
# ---------------------------------------------------------------------------

_QUIZ_CACHE_KEYS = ['quiz_questions:easy', 'quiz_questions:medium', 'quiz_questions:difficult']


def _invalidate_quiz_cache():
    for k in _QUIZ_CACHE_KEYS:
        _cache_manager.delete(k)


def _invalidate_scam_cache(scam_type=None):
    _cache_manager.delete('scam_definitions:all')
    if scam_type:
        _cache_manager.delete(f'scam_definitions:{scam_type}')


def _invalidate_practice_cache(scam_type=None):
    if scam_type:
        _cache_manager.delete(f'practice_quizzes:{scam_type}')
