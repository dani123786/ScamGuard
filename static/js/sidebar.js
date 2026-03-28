/**
 * sidebar.js — Sidebar toggle logic for all pages.
 * Handles desktop toggle, mobile overlay, backdrop, and active link highlighting.
 */
document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    const footer = document.querySelector('footer');

    // Create backdrop for mobile overlay
    const backdrop = document.createElement('div');
    backdrop.className = 'sidebar-backdrop';
    backdrop.id = 'sidebarBackdrop';
    document.body.appendChild(backdrop);

    function isMobile() {
        return window.innerWidth < 768;
    }

    function openMobileSidebar() {
        sidebar.classList.add('show');
        backdrop.classList.add('show');
        toggleBtn.classList.add('active');
    }

    function closeMobileSidebar() {
        sidebar.classList.remove('show');
        backdrop.classList.remove('show');
        toggleBtn.classList.remove('active');
    }

    function applyDesktopState() {
        sidebar.classList.remove('show');
        backdrop.classList.remove('show');
        const sidebarHidden = localStorage.getItem('sidebarHidden') === 'true';
        if (sidebarHidden) {
            sidebar.classList.add('hidden');
            mainContent.classList.add('expanded');
            if (footer) footer.classList.add('expanded');
            toggleBtn.classList.add('active');
        } else {
            sidebar.classList.remove('hidden');
            mainContent.classList.remove('expanded');
            if (footer) footer.classList.remove('expanded');
            toggleBtn.classList.remove('active');
        }
    }

    if (!isMobile()) {
        applyDesktopState();
    }

    toggleBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (isMobile()) {
            sidebar.classList.contains('show') ? closeMobileSidebar() : openMobileSidebar();
        } else {
            sidebar.classList.toggle('hidden');
            mainContent.classList.toggle('expanded');
            if (footer) footer.classList.toggle('expanded');
            toggleBtn.classList.toggle('active');
            localStorage.setItem('sidebarHidden', sidebar.classList.contains('hidden'));
        }
    });

    backdrop.addEventListener('click', closeMobileSidebar);

    window.addEventListener('resize', function () {
        if (isMobile()) {
            mainContent.classList.remove('expanded');
            if (footer) footer.classList.remove('expanded');
        } else {
            closeMobileSidebar();
            applyDesktopState();
        }
    });

    // Ctrl+B shortcut (desktop only)
    document.addEventListener('keydown', function (e) {
        if (e.ctrlKey && e.key === 'b') {
            e.preventDefault();
            toggleBtn.click();
        }
    });

    // Highlight active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar .nav-link').forEach(function (link) {
        const linkPath = new URL(link.href).pathname;
        link.classList.remove('active');
        if (
            currentPath === linkPath ||
            (currentPath.startsWith('/awareness/') && linkPath === '/awareness') ||
            (currentPath === '/' && linkPath === '/')
        ) {
            link.classList.add('active');
        }
    });
});