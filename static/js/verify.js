/**
 * verify.js — Scammer contact verification logic.
 */
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('verifyForm').addEventListener('submit', async function (e) {
        e.preventDefault();

        const query = document.getElementById('searchQuery').value.trim();
        const searchType = document.querySelector('input[name="searchType"]:checked').value;

        if (!query) { alert('Please enter an email or phone number to verify'); return; }

        document.getElementById('loadingState').style.display = 'block';
        document.getElementById('resultsContainer').style.display = 'none';
        document.getElementById('verifyBtn').disabled = true;

        try {
            const response = await fetch('/api/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, type: searchType })
            });
            const data = await response.json();
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('verifyBtn').disabled = false;
            response.ok ? displayVerifyResults(data) : displayVerifyError(data.message || 'Verification failed');
        } catch (error) {
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('verifyBtn').disabled = false;
            displayVerifyError('Network error. Please try again.');
        }
    });
});

function displayVerifyResults(data) {
    const container = document.getElementById('resultsContainer');
    container.style.display = 'block';

    if (!data.found) {
        container.innerHTML =
            '<div class="alert alert-success" role="alert">' +
            '<div class="d-flex align-items-center mb-3">' +
            '<i class="fas fa-check-circle fa-3x text-success me-3"></i>' +
            '<div><h4 class="alert-heading mb-1">No Reports Found</h4>' +
            '<p class="mb-0">This contact has not been reported in our database</p></div></div><hr>' +
            '<p class="mb-2"><strong>Searched:</strong> ' + escapeHtml(data.query) + '</p>' +
            '<p class="mb-0"><i class="fas fa-info-circle"></i> ' + data.recommendation + '</p></div>';
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        return;
    }

    const warningColor = data.warning_level === 'HIGH' ? 'danger' : data.warning_level === 'MEDIUM' ? 'warning' : 'info';
    const warningIcon = data.warning_level === 'HIGH' ? 'fa-exclamation-triangle' : 'fa-exclamation-circle';

    let html =
        '<div class="alert alert-' + warningColor + '" role="alert">' +
        '<div class="d-flex align-items-center mb-3">' +
        '<i class="fas ' + warningIcon + ' fa-3x me-3"></i>' +
        '<div><h4 class="alert-heading mb-1">⚠️ SCAMMER ALERT</h4>' +
        '<p class="mb-0">This contact has been reported ' + data.total_reports + ' time(s)</p></div></div><hr>' +
        '<p class="mb-2"><strong>Contact:</strong> ' + escapeHtml(data.query) + '</p>' +
        '<p class="mb-0">' + data.recommendation + '</p></div>' +
        '<div class="detail-card mt-3"><h5 class="mb-3"><i class="fas fa-chart-bar"></i> Report Statistics</h5>' +
        '<div class="row">' +
        '<div class="col-md-6 mb-3"><div class="stat-box bg-light p-3 rounded"><h6 class="text-muted mb-1">Total Reports</h6><h3 class="mb-0 text-primary">' + data.total_reports + '</h3></div></div>' +
        '<div class="col-md-6 mb-3"><div class="stat-box bg-light p-3 rounded"><h6 class="text-muted mb-1">High Severity</h6><h3 class="mb-0 text-danger">' + data.high_severity_count + '</h3></div></div>' +
        '<div class="col-md-6 mb-3"><div class="stat-box bg-light p-3 rounded"><h6 class="text-muted mb-1">Most Common Scam</h6><p class="mb-0 fw-bold">' + data.most_common_scam + '</p></div></div>' +
        '<div class="col-md-6 mb-3"><div class="stat-box bg-light p-3 rounded"><h6 class="text-muted mb-1">Victims Lost Money</h6><p class="mb-0 fw-bold">' + data.victims_lost_money + ' victim(s)</p></div></div>' +
        '</div>' +
        (data.total_money_lost > 0 ? '<div class="alert alert-danger mt-3"><i class="fas fa-dollar-sign me-2"></i><strong>Total Money Lost:</strong> $' + data.total_money_lost.toLocaleString() + '</div>' : '') +
        '<p class="mb-2"><strong><i class="fas fa-calendar"></i> Most Recent Report:</strong> ' + formatDate(data.most_recent_report) + '</p>' +
        '<p class="mb-0"><strong><i class="fas fa-phone"></i> Contact Methods Used:</strong> ' + data.contact_methods.join(', ') + '</p></div>';

    if (data.sample_reports && data.sample_reports.length > 0) {
        html += '<div class="detail-card mt-3"><h5 class="mb-3"><i class="fas fa-file-alt"></i> Recent Reports</h5>';
        data.sample_reports.forEach(function (report, index) {
            html +=
                '<div class="card mb-3"><div class="card-body">' +
                '<div class="d-flex justify-content-between align-items-start mb-2">' +
                '<h6 class="card-subtitle text-muted">Report #' + (index + 1) + '</h6>' +
                '<span class="badge bg-' + (report.lost_money ? 'danger' : 'secondary') + '">' + (report.lost_money ? 'Money Lost' : 'No Money Lost') + '</span></div>' +
                '<p class="mb-2"><strong>Type:</strong> ' + report.scam_type + '</p>' +
                '<p class="mb-2"><strong>Method:</strong> ' + report.contact_method + '</p>' +
                '<p class="mb-2"><strong>Date:</strong> ' + formatDate(report.date) + '</p>' +
                '<p class="mb-0"><strong>Description:</strong> ' + escapeHtml(report.description) + '</p>' +
                '</div></div>';
        });
        html += '</div>';
    }

    container.innerHTML = html;
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function displayVerifyError(message) {
    const container = document.getElementById('resultsContainer');
    container.style.display = 'block';
    container.innerHTML = '<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle me-2"></i><strong>Error:</strong> ' + escapeHtml(message) + '</div>';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString || dateString === 'Unknown') return 'Unknown';
    try {
        return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    } catch (e) { return dateString; }
}