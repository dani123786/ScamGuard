"""Admin authentication routes + login page."""
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, session
import routes.extensions as ext

auth = Blueprint('auth', __name__)


@auth.route('/admin/login')
def admin_login_page():
    """GET /admin/login — show the admin login page."""
    user = ext._auth_get_current_user() if ext._AUTH_AVAILABLE else None
    if user:
        return redirect('/admin/reports')
    return render_template('admin_login.html')


@auth.route('/admin/auth/login', methods=['POST'])
def admin_auth_login():
    """POST /admin/auth/login — authenticate and create a session."""
    data = request.get_json(force=True, silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'error': 'username and password are required'}), 400

    user = ext._auth_login_user(username, password, ext.supabase_client) if ext._AUTH_AVAILABLE else None

    if user is None:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    session['login_time'] = datetime.utcnow().isoformat()
    session.permanent = False

    return jsonify({'success': True, 'role': user['role']})


@auth.route('/admin/auth/logout', methods=['POST'])
def admin_auth_logout():
    """POST /admin/auth/logout — clear the session and redirect to login."""
    username = session.get('username', 'anonymous')
    if ext._AUTH_AVAILABLE:
        ext._auth_log_auth_event('LOGOUT', username, True)
        ext._auth_clear_session()
    else:
        session.clear()
    return redirect('/admin/login')


@auth.route('/admin/auth/me', methods=['GET'])
def admin_auth_me():
    """GET /admin/auth/me — return current user info or 401."""
    user = ext._auth_get_current_user() if ext._AUTH_AVAILABLE else None
    if user is None:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'user': user})


@auth.route('/admin/auth/csrf-token', methods=['GET'])
def admin_auth_csrf_token():
    """GET /admin/auth/csrf-token — return a CSRF token for write operations.

    FIX: Now requires an authenticated session. Unauthenticated requests
    receive 401 instead of a usable token.
    """
    user = ext._auth_get_current_user() if ext._AUTH_AVAILABLE else None
    if user is None:
        return jsonify({'error': 'Authentication required'}), 401

    token = ext._auth_generate_csrf_token() if ext._AUTH_AVAILABLE else 'csrf-unavailable'
    return jsonify({'csrf_token': token})
