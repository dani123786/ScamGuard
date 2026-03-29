/**
 * report.js — Scam report form submission logic.
 * FIX: After submission, display the AI analysis result to the user.
 */
function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
}

function buildSafeList(items) {
    return Array.isArray(items) && items.length
        ? `<ul class="mb-0 ps-3">${items.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
        : '<span class="text-muted">None detected</span>';
}

function safeText(value, fallback) {
    const text = value == null ? '' : String(value).trim();
    return escapeHtml(text || fallback);
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[name="lost-money"]').forEach(function (radio) {
        radio.addEventListener('change', function (e) {
            document.getElementById('amount-section').style.display =
                e.target.value === 'yes' ? 'block' : 'none';
        });
    });

    document.getElementById('report-form').addEventListener('submit', async function (e) {
        e.preventDefault();

        const submitBtn = this.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting & Analyzing…';

        const formData = {
            scam_type: document.getElementById('scam-type').value,
            contact_method: document.getElementById('contact-method').value,
            description: document.getElementById('description').value,
            scammer_contact: document.getElementById('scammer-contact').value,
            lost_money: document.querySelector('input[name="lost-money"]:checked').value,
            amount: document.getElementById('amount').value,
            reporter_email: document.getElementById('reporter-email').value,
            incident_date: document.getElementById('incident-date').value
        };

        try {
            const response = await fetch('/api/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById('report-form').style.display = 'none';

                // Build the success + AI analysis block
                const successEl = document.getElementById('success-message');
                if (result.ai_analysis) {
                    const ai = result.ai_analysis;
                    const severityClass = {
                        CRITICAL: 'danger',
                        HIGH:     'warning',
                        MEDIUM:   'primary',
                        LOW:      'success'
                    }[ai.severity] || 'secondary';

                    const severityIcon = {
                        CRITICAL: '🔴',
                        HIGH:     '🟠',
                        MEDIUM:   '🟡',
                        LOW:      '🟢'
                    }[ai.severity] || '⚪';

                    const summary = safeText(ai.summary, 'We reviewed your report and found suspicious behavior that should be treated cautiously.');
                    const victimAdvice = safeText(ai.victim_advice, 'Stop contact, save evidence, and verify through official channels.');
                    const communityImpact = safeText(ai.community_impact, 'Your report helps warn other people about similar scam tactics.');
                    const category = safeText(ai.scam_category, 'Suspicious Activity');

                    // Build common patterns list
                    const patterns = buildSafeList(ai.common_patterns);

                    // Build red flags list
                    const flags = buildSafeList(ai.red_flags_identified);

                    // Build prevention tips list
                    const tips = Array.isArray(ai.prevention_tips) && ai.prevention_tips.length
                        ? `<ul class="mb-0 ps-3">${ai.prevention_tips.map(t => `<li>${escapeHtml(t)}</li>`).join('')}</ul>`
                        : buildSafeList([]);

                    // Authorities section
                    let authoritiesHtml = '';
                    if (ai.should_report_to_authorities === 'YES') {
                        const auths = Array.isArray(ai.authorities_to_contact) && ai.authorities_to_contact.length
                            ? ai.authorities_to_contact.map(a => `<span class="badge bg-danger me-1">${escapeHtml(a)}</span>`).join('')
                            : '';
                        authoritiesHtml = `
                            <div class="alert alert-danger py-2 mt-2 mb-0">
                                <strong>⚠️ Report to Authorities</strong>
                                ${auths ? `<div class="mt-1">${auths}</div>` : ''}
                            </div>`;
                    }

                    successEl.innerHTML = `
                        <div class="alert alert-success mb-4">
                            <h5 class="alert-heading"><i class="fas fa-check-circle me-2"></i>Report Submitted Successfully</h5>
                            <p class="mb-0">${escapeHtml(result.message)}</p>
                        </div>

                        <div class="card border-0 shadow-sm mb-4" style="background:rgba(167,139,250,0.06);border:1px solid rgba(167,139,250,0.2)!important;">
                            <div class="card-body">
                                <h5 class="mb-3" style="color:#a78bfa;">
                                    <i class="fas fa-robot me-2"></i>AI Analysis Results
                                </h5>

                                <div class="d-flex align-items-center gap-3 mb-3 flex-wrap">
                                    <span class="badge bg-${severityClass} fs-6 px-3 py-2">
                                        ${severityIcon} ${escapeHtml(ai.severity || 'UNKNOWN')} Risk
                                    </span>
                                    <span class="badge bg-secondary px-3 py-2">${category}</span>
                                </div>

                                <div class="mb-3 p-3 rounded" style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);">
                                    <small class="text-muted d-block mb-1 text-uppercase fw-semibold" style="font-size:0.7rem;letter-spacing:.07em;">
                                        <i class="fas fa-brain me-1"></i>Overall Analysis
                                    </small>
                                    <span style="font-size:.9rem;line-height:1.65;">${summary}</span>
                                </div>

                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <div class="p-3 rounded" style="background:rgba(255,255,255,0.04);">
                                            <small class="text-muted d-block mb-1 text-uppercase fw-semibold" style="font-size:0.7rem;letter-spacing:.07em;">
                                                <i class="fas fa-user-shield me-1"></i>Advice For You
                                            </small>
                                            <span style="font-size:.875rem;">${victimAdvice}</span>
                                        </div>
                                    </div>

                                    <div class="col-md-6">
                                        <div class="p-3 rounded" style="background:rgba(255,255,255,0.04);">
                                            <small class="text-muted d-block mb-1 text-uppercase fw-semibold" style="font-size:0.7rem;letter-spacing:.07em;">
                                                <i class="fas fa-users me-1"></i>Community Impact
                                            </small>
                                            <span style="font-size:.875rem;">${communityImpact}</span>
                                        </div>
                                    </div>

                                    <div class="col-md-6">
                                        <div class="p-3 rounded" style="background:rgba(255,255,255,0.04);">
                                            <small class="text-muted d-block mb-1 text-uppercase fw-semibold" style="font-size:0.7rem;letter-spacing:.07em;">
                                                <i class="fas fa-flag me-1"></i>Red Flags Identified
                                            </small>
                                            <div style="font-size:.875rem;">${flags}</div>
                                        </div>
                                    </div>

                                    <div class="col-md-6">
                                        <div class="p-3 rounded" style="background:rgba(255,255,255,0.04);">
                                            <small class="text-muted d-block mb-1 text-uppercase fw-semibold" style="font-size:0.7rem;letter-spacing:.07em;">
                                                <i class="fas fa-search me-1"></i>Common Patterns
                                            </small>
                                            <div style="font-size:.875rem;">${patterns}</div>
                                        </div>
                                    </div>

                                    <div class="col-12">
                                        <div class="p-3 rounded" style="background:rgba(255,255,255,0.04);">
                                            <small class="text-muted d-block mb-1 text-uppercase fw-semibold" style="font-size:0.7rem;letter-spacing:.07em;">
                                                <i class="fas fa-lightbulb me-1"></i>Prevention Tips
                                            </small>
                                            <div style="font-size:.875rem;">${tips}</div>
                                        </div>
                                    </div>
                                </div>

                                ${authoritiesHtml}
                            </div>
                        </div>`;
                } else {
                    // No AI analysis — show plain success
                    successEl.innerHTML = `
                        <div class="alert alert-success">
                            <h5 class="alert-heading"><i class="fas fa-check-circle me-2"></i>Report Submitted Successfully</h5>
                            <p class="mb-0">${escapeHtml(result.message)}</p>
                        </div>`;
                }

                successEl.style.display = 'block';
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                // Submission failed — re-enable button and show error
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                alert(result.error || 'Submission failed. Please try again.');
            }
        } catch (err) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            alert('Network error. Please check your connection and try again.');
        }
    });
});
