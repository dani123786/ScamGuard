/**
 * admin_login.js — Admin login form submission logic.
 */
document.getElementById('login-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const btn = document.getElementById('btn');
    const errDiv = document.getElementById('error-msg');
    const errText = document.getElementById('error-text');
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Signing in...';
    errDiv.classList.add('d-none');

    try {
        const resp = await fetch('/admin/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await resp.json();

        if (resp.ok && data.success) {
            window.location.href = '/admin/reports';
        } else {
            errText.textContent = data.error || 'Invalid username or password';
            errDiv.classList.remove('d-none');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Sign In';
        }
    } catch (err) {
        errText.textContent = 'Connection error. Please try again.';
        errDiv.classList.remove('d-none');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Sign In';
    }
});
