/**
 * stats.js — Live community statistics for the home page.
 * Fetches /api/stats, animates numbers, and auto-refreshes every 30 seconds.
 */

async function loadLiveStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        const statusIcon = document.getElementById('db-status-icon');
        const statusDot  = document.getElementById('db-dot');
        const statusText = document.getElementById('db-status-text');

        if (stats.database_connected) {
            if (statusIcon) statusIcon.className = 'fas fa-circle text-success';
            if (statusDot)  statusDot.style.background = '#06d6a0';
            if (statusText) statusText.textContent = 'Connected to live database';
        } else {
            if (statusIcon) statusIcon.className = 'fas fa-circle text-danger';
            if (statusDot)  statusDot.style.background = '#fb4f4f';
            if (statusText) statusText.textContent = 'Database offline — showing cached data';
        }

        document.querySelectorAll('[id^="stat-loader-"]').forEach(function (el) {
            el.style.display = 'none';
        });

        const totalReportsEl = document.getElementById('stat-total-reports');
        totalReportsEl.style.display = 'block';
        animateNumber(totalReportsEl, 0, stats.total_reports, 1000);

        const highRiskEl = document.getElementById('stat-high-risk');
        highRiskEl.style.display = 'block';
        animateNumber(highRiskEl, 0, stats.high_risk_reports, 1000);

        const moneyLostEl = document.getElementById('stat-money-lost');
        moneyLostEl.style.display = 'block';
        animateNumber(moneyLostEl, 0, stats.total_money_lost, 1000, true);
        setTimeout(function () { autoShrinkStat(moneyLostEl); }, 1100);

        const thisMonthEl = document.getElementById('stat-this-month');
        thisMonthEl.style.display = 'block';
        animateNumber(thisMonthEl, 0, stats.reports_this_month, 1000);

        document.getElementById('stat-top-scam').textContent = stats.top_scam_type;
        document.getElementById('stat-contact-method').textContent = stats.most_common_contact_method;

    } catch (error) {
        console.error('Error loading stats:', error);
        const statusIcon = document.getElementById('db-status-icon');
        const statusDot  = document.getElementById('db-dot');
        const statusText = document.getElementById('db-status-text');
        if (statusIcon) statusIcon.className = 'fas fa-circle text-danger';
        if (statusDot)  statusDot.style.background = '#fb4f4f';
        if (statusText) statusText.textContent = 'Failed to load statistics';

        document.querySelectorAll('[id^="stat-loader-"]').forEach(function (el) {
            el.style.display = 'none';
        });

        ['stat-total-reports', 'stat-high-risk', 'stat-money-lost', 'stat-this-month'].forEach(function (id) {
            const el = document.getElementById(id);
            el.style.display = 'block';
            el.textContent = 'N/A';
        });
        document.getElementById('stat-top-scam').textContent = 'N/A';
        document.getElementById('stat-contact-method').textContent = 'N/A';
    }
}

function animateNumber(element, start, end, duration, isCurrency) {
    const startTime = performance.now();
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutQuad = progress * (2 - progress);
        const current = Math.floor(start + (end - start) * easeOutQuad);
        element.textContent = isCurrency ? '$' + current.toLocaleString() : current.toLocaleString();
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

function autoShrinkStat(element) {
    const len = element.textContent.length;
    if (len > 8) {
        element.style.fontSize = '1.8rem';
    } else if (len > 6) {
        element.style.fontSize = '2.2rem';
    } else {
        element.style.fontSize = '';
    }
}

document.addEventListener('DOMContentLoaded', loadLiveStats);
setInterval(loadLiveStats, 30000);