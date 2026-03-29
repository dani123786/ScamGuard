/**
 * auth.js — JWT token management for authenticated requests
 */

// Function to get auth headers with JWT token
function getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// Function to check if user is authenticated
function isAuthenticated() {
    const token = localStorage.getItem('auth_token');
    if (!token) return false;

    try {
        // Basic check if token exists and isn't expired
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Date.now() / 1000;
        return payload.exp > currentTime;
    } catch (e) {
        return false;
    }
}

// Function to logout
function logout() {
    localStorage.removeItem('auth_token');
    window.location.href = '/admin/login';
}

// Make functions globally available
window.AuthUtils = {
    getAuthHeaders,
    isAuthenticated,
    logout
};