/**
 * checker.js — AI Scam Checker logic.
 */

function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
}

function normalizeText(value, fallback) {
    const text = value == null ? '' : String(value).trim();
    return text || fallback;
}

function normalizeList(value) {
    if (Array.isArray(value)) {
        return value.map(function (item) { return normalizeText(item, ''); }).filter(Boolean);
    }
    const text = normalizeText(value, '');
    return text ? [text] : [];
}

function normalizeScore(value) {
    const match = String(value == null ? '' : value).match(/-?\d+/);
    const parsed = match ? parseInt(match[0], 10) : 0;
    return Math.max(0, Math.min(100, Number.isNaN(parsed) ? 0 : parsed));
}

async function checkUrl() {
    const url = document.getElementById('url-content').value.trim();
    if (!url) { _showError('Please enter a URL to analyze.'); return; }
    _setLoading('url-btn', true);
    let results = null;
    try {
        const response = await fetch('/api/check/url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await response.json();
        if (data.error) { _showApiError(data); }
        else { results = data; results._is_url = true; }
    } catch (err) {
        _showError('Connection error. Please check your internet and try again.');
    } finally {
        _setLoading('url-btn', false);
    }
    if (results) displayResults(results);
}

async function checkContent(type) {
    const content = document.getElementById(type === 'email' ? 'email-content' : 'message-content').value;
    if (!content.trim()) { _showError('Please enter content to analyze.'); return; }
    const btnId = type === 'email' ? 'email-btn' : 'message-btn';
    _setLoading(btnId, true);
    let results = null;
    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, content })
        });
        const data = await response.json();
        if (data.error) { _showApiError(data); }
        else { results = data; }
    } catch (err) {
        _showError('Connection error. Please check your internet and try again.');
    } finally {
        _setLoading(btnId, false);
    }
    if (results) displayResults(results);
}

function _setLoading(btnId, loading) {
    document.getElementById('loading-indicator').style.display = loading ? 'block' : 'none';
    if (loading) document.getElementById('results-container').style.display = 'none';
    const btn = document.getElementById(btnId);
    if (btn) btn.disabled = loading;
}

function _showError(msg) {
    const container = document.getElementById('results-container');
    document.getElementById('results-content').innerHTML =
        '<div style="background:rgba(251,79,79,0.08);border:1px solid rgba(251,79,79,0.2);border-radius:12px;padding:20px 24px;color:#f09595;font-size:0.9rem;">' +
        '<i class="fas fa-exclamation-circle" style="margin-right:8px;"></i>' + msg + '</div>';
    container.style.display = 'block';
}

function _showApiError(data) {
    const details = (data.details || data.error || '').toString();
    let msg = 'AI analysis failed. Please try again in a moment.';
    if (details.includes('Rate limit') || details.includes('429') || details.includes('RESOURCE_EXHAUSTED')) {
        msg = 'The AI service is temporarily rate-limited. Please wait 1–2 minutes and try again.';
    } else if (details.includes('API_KEY') || details.includes('invalid') || details.includes('not set')) {
        msg = 'API key issue. Please check your GEMINI_API_KEY configuration.';
    } else if (details.includes('503') || details.includes('unavailable')) {
        msg = 'The AI service is temporarily unavailable. Please try again shortly.';
    }
    _showError(msg);
}

function displayResults(r) {
    const container = document.getElementById('results-container');
    const content = document.getElementById('results-content');

    const score = normalizeScore(r.risk_score);
    const level = normalizeText(r.risk_level, 'UNKNOWN').toUpperCase();
    const summary = escapeHtml(normalizeText(r.summary, 'No summary was returned.'));
    const recommendation = escapeHtml(normalizeText(r.recommendation, 'Exercise caution and verify independently.'));
    const scamType = escapeHtml(normalizeText(r.scam_type, 'Unable to analyse'));
    const confidence = escapeHtml(normalizeText(r.confidence, 'LOW').toUpperCase());
    const goal = escapeHtml(normalizeText(r.what_scammer_wants, 'N/A'));
    const redFlags = normalizeList(r.red_flags);
    const legitimateAspects = normalizeList(r.legitimate_aspects);

    const palette = {
        HIGH:   { stroke: '#fb4f4f', bg: 'rgba(251,79,79,0.1)',  border: 'rgba(251,79,79,0.25)',  text: '#fb4f4f', label: 'HIGH RISK' },
        MEDIUM: { stroke: '#f59e0b', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.25)', text: '#f59e0b', label: 'MEDIUM RISK' },
        LOW:    { stroke: '#06d6a0', bg: 'rgba(6,214,160,0.1)',  border: 'rgba(6,214,160,0.25)', text: '#06d6a0', label: 'LOW RISK' },
        UNKNOWN:{ stroke: '#94a3b8', bg: 'rgba(148,163,184,0.1)', border: 'rgba(148,163,184,0.25)', text: '#94a3b8', label: 'UNKNOWN RISK' },
    };
    const p = palette[level] || palette.UNKNOWN;

    const R = 40, circ = 2 * Math.PI * R;
    const offset = circ * (1 - score / 100);
    const ring =
        '<svg width="110" height="110" viewBox="0 0 110 110">' +
        '<circle cx="55" cy="55" r="' + R + '" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>' +
        '<circle cx="55" cy="55" r="' + R + '" fill="none" stroke="' + p.stroke + '" stroke-width="8"' +
        ' stroke-dasharray="' + circ + '" stroke-dashoffset="' + offset + '"' +
        ' transform="rotate(-90 55 55)" style="transition:stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1);"/>' +
        '</svg>' +
        '<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">' +
        '<span style="font-family:Outfit,sans-serif;font-size:1.5rem;font-weight:700;color:' + p.stroke + ';line-height:1;">' + score + '</span>' +
        '<span style="font-size:0.65rem;color:#7a8aaa;margin-top:2px;">/ 100</span></div>';

    let flagsHTML = '';
    if (redFlags.length) {
        flagsHTML = '<div class="res-section"><div class="res-section-title" style="color:#fb4f4f;"><i class="fas fa-exclamation-triangle"></i> Red Flags Detected</div>' +
            '<ul class="res-list res-list-danger">' + redFlags.map(function(f){ return '<li><i class="fas fa-times-circle"></i>' + escapeHtml(f) + '</li>'; }).join('') + '</ul></div>';
    }

    let legitHTML = '';
    if (legitimateAspects.length) {
        legitHTML = '<div class="res-section"><div class="res-section-title" style="color:#06d6a0;"><i class="fas fa-check-circle"></i> Legitimate Aspects</div>' +
            '<ul class="res-list res-list-success">' + legitimateAspects.map(function(f){ return '<li><i class="fas fa-check"></i>' + escapeHtml(f) + '</li>'; }).join('') + '</ul></div>';
    }

    let goalHTML = '';
    if (goal !== 'N/A') {
        goalHTML = '<div class="res-section"><div class="res-section-title"><i class="fas fa-crosshairs"></i> What the Scammer Wants</div>' +
            '<p class="res-text">' + goal + '</p></div>';
    }

    let domainHTML = '';
    if (r._is_url && r.domain_analysis) {
        var da = r.domain_analysis;
        var domain = escapeHtml(normalizeText(da.domain, normalizeText(r.analyzed_url, 'N/A')));
        var impersonating = normalizeText(da.is_impersonating, 'UNKNOWN').toUpperCase();
        var brand = escapeHtml(normalizeText(da.impersonating_brand, 'None detected'));
        var patterns = normalizeList(da.suspicious_patterns).map(escapeHtml);
        domainHTML = '<div class="res-section"><div class="res-section-title"><i class="fas fa-globe"></i> Domain Analysis</div>' +
            '<div class="res-kv">' +
            '<span class="res-key">Domain</span><span class="res-val">' + domain + '</span>' +
            '<span class="res-key">Impersonating</span><span class="res-val" style="color:' + (impersonating === 'YES' ? '#fb4f4f' : '#06d6a0') + '">' +
            (impersonating === 'YES' ? brand : 'None detected') + '</span>' +
            (patterns.length ? '<span class="res-key">Patterns</span><span class="res-val">' + patterns.join(', ') + '</span>' : '') +
            '</div></div>';
    }

    var scamBadge = (normalizeText(r.scam_type, '') && normalizeText(r.scam_type, '') !== 'None Detected')
        ? '<span class="res-badge"><i class="fas fa-tag"></i>' + scamType + '</span>' +
          '<span class="res-badge">Confidence: ' + confidence + '</span>'
        : '<span class="res-badge" style="color:#06d6a0;border-color:rgba(6,214,160,0.2);"><i class="fas fa-shield-alt"></i> No Scam Detected</span>';

    content.innerHTML =
        '<style>' +
        '.res-card{background:#0e1628;border:1px solid rgba(255,255,255,0.07);border-radius:16px;overflow:hidden;}' +
        '.res-header{display:flex;align-items:center;justify-content:space-between;padding:22px 24px;border-bottom:1px solid rgba(255,255,255,0.06);background:' + p.bg + ';border-top:3px solid ' + p.stroke + ';flex-wrap:wrap;gap:16px;}' +
        '.res-risk-label{font-family:Outfit,sans-serif;font-size:1.4rem;font-weight:800;color:' + p.stroke + ';letter-spacing:-0.02em;}' +
        '.res-badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;}' +
        '.res-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:6px;font-size:0.75rem;font-weight:500;background:rgba(255,255,255,0.06);color:#c0c8d8;border:1px solid rgba(255,255,255,0.08);}' +
        '.res-badge.ai{background:rgba(99,102,241,0.15);color:#a5b4fc;border-color:rgba(99,102,241,0.25);}' +
        '.res-ring{position:relative;width:110px;height:110px;flex-shrink:0;}' +
        '.res-body{padding:20px 24px;display:flex;flex-direction:column;gap:0;}' +
        '.res-section{padding:16px 0;border-bottom:1px solid rgba(255,255,255,0.05);}' +
        '.res-section:last-child{border-bottom:none;}' +
        '.res-section-title{font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.07em;color:#7a8aaa;margin-bottom:10px;display:flex;align-items:center;gap:7px;}' +
        '.res-text{font-size:0.9rem;color:#c0c8d8;line-height:1.6;margin:0;}' +
        '.res-list{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:7px;}' +
        '.res-list li{display:flex;align-items:flex-start;gap:9px;font-size:0.875rem;line-height:1.5;padding:8px 12px;border-radius:8px;}' +
        '.res-list li i{flex-shrink:0;margin-top:2px;font-size:12px;}' +
        '.res-list-danger li{background:rgba(251,79,79,0.07);color:#f09595;border:1px solid rgba(251,79,79,0.12);}' +
        '.res-list-danger li i{color:#fb4f4f;}' +
        '.res-list-success li{background:rgba(6,214,160,0.07);color:#9fe1cb;border:1px solid rgba(6,214,160,0.12);}' +
        '.res-list-success li i{color:#06d6a0;}' +
        '.res-recommendation{padding:14px 16px;border-radius:10px;font-size:0.875rem;line-height:1.6;background:' + p.bg + ';border:1px solid ' + p.border + ';color:#e8edf8;}' +
        '.res-kv{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;font-size:0.875rem;}' +
        '.res-key{color:#7a8aaa;font-weight:500;}' +
        '.res-val{color:#e8edf8;}' +
        '.btn-reanalyze{display:inline-flex;align-items:center;gap:7px;padding:9px 20px;background:transparent;border:1px solid rgba(255,255,255,0.1);border-radius:8px;color:#7a8aaa;font-size:0.8rem;cursor:pointer;transition:all 0.2s;margin-top:16px;}' +
        '.btn-reanalyze:hover{border-color:rgba(6,214,160,0.3);color:#06d6a0;background:rgba(6,214,160,0.05);}' +
        '</style>' +
        '<div class="res-card">' +
        '<div class="res-header">' +
        '<div><div class="res-risk-label">' + p.label + '</div>' +
        '<div class="res-badges">' +
        (r.ai_powered ? '<span class="res-badge ai"><i class="fas fa-robot"></i> Gemini AI</span>' : '') +
        scamBadge + '</div></div>' +
        '<div class="res-ring">' + ring + '</div></div>' +
        '<div class="res-body">' +
        '<div class="res-section"><div class="res-section-title"><i class="fas fa-brain"></i> AI Summary</div><p class="res-text">' + summary + '</p></div>' +
        flagsHTML + legitHTML + goalHTML + domainHTML +
        '<div class="res-section"><div class="res-section-title"><i class="fas fa-lightbulb"></i> Recommendation</div>' +
        '<div class="res-recommendation">' + recommendation + '</div></div>' +
        '<div><button class="btn-reanalyze" onclick="document.getElementById(\'results-container\').style.display=\'none\'"><i class="fas fa-arrow-left"></i> Analyse Another</button></div>' +
        '</div></div>';

    container.style.display = 'block';
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
