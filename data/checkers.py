import re
import json
import os
import time
from urllib.parse import unquote, urlsplit
from dotenv import load_dotenv

# Force the import - if this fails, Render will show us the REAL error in the logs
from google import genai
from google.genai import types

load_dotenv()

# We set this to True because the import above didn't crash the app
GEMINI_AVAILABLE = True

# ---------------------------------------------------------------------------
# Truncated JSON recovery
# Handles the case where gemini-2.5-flash cuts off mid-response
# ---------------------------------------------------------------------------

def _recover_truncated_json(text: str) -> dict:
    """
    Try to salvage a truncated JSON response by extracting all complete
    top-level key-value pairs that were received before the cutoff.
    Returns a partial dict, or raises ValueError if nothing usable.
    """
    # Extract the content between the outermost opening { and end of text
    start = text.find('{')
    if start == -1:
        raise ValueError("No opening brace found")

    partial = text[start:]

    # Collect all complete "key": value pairs we can find
    recovered = {}

    # Match simple string values: "key": "value"
    for m in re.finditer(r'"([^"]+)"\s*:\s*"([^"]*)"', partial):
        recovered[m.group(1)] = m.group(2)

    # Match numeric values: "key": 42
    for m in re.finditer(r'"([^"]+)"\s*:\s*(-?\d+(?:\.\d+)?)', partial):
        key = m.group(1)
        if key not in recovered:
            try:
                recovered[key] = int(m.group(2))
            except ValueError:
                recovered[key] = float(m.group(2))

    # Match array values (best effort): "key": ["item1", "item2"]
    for m in re.finditer(r'"([^"]+)"\s*:\s*\[([^\]]*)\]', partial):
        key = m.group(1)
        if key not in recovered:
            items = re.findall(r'"([^"]*)"', m.group(2))
            recovered[key] = items

    # Match nested object values (domain_analysis etc)
    for m in re.finditer(r'"([^"]+)"\s*:\s*\{([^}]*)\}', partial):
        key = m.group(1)
        if key not in recovered:
            nested = {}
            for nm in re.finditer(r'"([^"]+)"\s*:\s*"([^"]*)"', m.group(2)):
                nested[nm.group(1)] = nm.group(2)
            if nested:
                recovered[key] = nested

    if not recovered:
        raise ValueError("No key-value pairs could be recovered")

    return recovered


# ---------------------------------------------------------------------------
# Robust JSON parser with truncation recovery
# ---------------------------------------------------------------------------

def _robust_json_parse(raw_text: str) -> dict:
    """
    Parse JSON from AI output. Handles: markdown fences, preamble text,
    trailing commas, unquoted keys, Python literals, and truncated responses.
    """
    text = raw_text.strip()

    def _clean(s):
        # Strip markdown fences
        s = re.sub(r'^```[a-zA-Z]*\r?\n?', '', s, flags=re.MULTILINE)
        s = re.sub(r'\r?\n?```\s*$', '', s, flags=re.MULTILINE)
        s = s.strip()
        # Extract outermost { ... }
        brace_match = re.search(r'\{[\s\S]*\}', s)
        if brace_match:
            s = brace_match.group()
        # Remove JS comments
        s = re.sub(r'//[^\n"]*(?=\n|$)', '', s)
        s = re.sub(r'/\*[\s\S]*?\*/', '', s)
        # Remove trailing commas
        s = re.sub(r',\s*([}\]])', r'\1', s)
        # Python literals
        s = re.sub(r'\bNone\b', 'null', s)
        s = re.sub(r'\bTrue\b', 'true', s)
        s = re.sub(r'\bFalse\b', 'false', s)
        return s.strip()

    # Strategy 1: parse as-is
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 2: clean then parse
    try:
        return json.loads(_clean(text))
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 3: extract { ... } from original, then clean & parse
    bm = re.search(r'\{[\s\S]*\}', text)
    if bm:
        try:
            return json.loads(_clean(bm.group()))
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 4: truncated JSON recovery (THE KEY NEW FIX)
    # This handles the case where gemini-2.5-flash cuts off mid-response
    # leaving no closing } due to free-tier rate limiting
    try:
        partial = _recover_truncated_json(text)
        print(f"[AI] Recovered {len(partial)} fields from truncated response: {list(partial.keys())}")
        return partial
    except (ValueError, Exception):
        pass

    raise json.JSONDecodeError("No JSON object found in AI response", text, 0)


# ---------------------------------------------------------------------------
# System instruction — forces JSON output at model level
# ---------------------------------------------------------------------------

_SYSTEM_INSTRUCTION = (
    "You are a JSON API. Output ONLY a valid JSON object. "
    "No markdown, no code fences, no text before or after. "
    "Start your response with { and end with }. "
    "Never truncate or omit fields. Complete every field fully."
)

# ---------------------------------------------------------------------------
# Models — gemini-2.5-flash first since it's the only one accessible
# on most free-tier API keys. Others kept as fallback.
# ---------------------------------------------------------------------------

_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
    'gemini-1.5-flash',
]


def _call_gemini(prompt: str, max_tokens: int = 600) -> dict:
    """
    Call Gemini API. Tries response_mime_type first (cleanest JSON),
    falls back to plain text generation if that returns empty.
    """
    if not GEMINI_AVAILABLE:
        raise Exception("Google GenAI package not installed")

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or len(api_key) < 20:
        raise Exception("GEMINI_API_KEY not set or invalid")

    client = genai.Client(api_key=api_key)
    last_error = None

    for model_name in _MODELS:
        # --- Attempt A: with response_mime_type (cleanest, no markdown) ---
        for attempt in range(2):
            try:
                print(f"[AI] Trying {model_name} with mime_type (attempt {attempt+1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=max_tokens,
                        system_instruction=_SYSTEM_INSTRUCTION,
                        response_mime_type='application/json',
                    ),
                )
                raw_text = (response.text or '').strip()
                print(f"[AI] {model_name}/mime returned {len(raw_text)} chars")

                if not raw_text:
                    print(f"[!] Empty response with mime_type — will retry without it")
                    break  # break inner loop, fall through to Attempt B

                result = _robust_json_parse(raw_text)
                print(f"[AI] Success with {model_name} (mime_type)")
                result['model_used'] = model_name
                return result

            except json.JSONDecodeError as e:
                if attempt == 0:
                    time.sleep(1)
                    continue
                last_error = f"JSON parse failed ({model_name}/mime): {e}"
                break

            except Exception as e:
                err = str(e)
                print(f"[!] {model_name}/mime error: {err[:120]}")
                if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                    last_error = f"Rate limit: {model_name}"
                    break  # skip this model entirely
                if '404' in err or 'not found' in err.lower():
                    last_error = f"Model unavailable: {model_name}"
                    break  # skip this model entirely
                if attempt == 0:
                    time.sleep(1)
                    continue
                last_error = f"Error ({model_name}/mime): {err[:80]}"
                break

        else:
            # Inner loop completed normally (no break) — means rate limit or 404, skip model
            continue

        # --- Attempt B: without response_mime_type (fallback) ---
        for attempt in range(2):
            try:
                print(f"[AI] Trying {model_name} plain text (attempt {attempt+1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=max_tokens,
                        system_instruction=_SYSTEM_INSTRUCTION,
                    ),
                )
                raw_text = (response.text or '').strip()
                preview = repr(raw_text[:120]) if raw_text else '<EMPTY>'
                print(f"[AI] {model_name}/plain returned {len(raw_text)} chars: {preview}")

                if not raw_text:
                    raise json.JSONDecodeError("Empty response", "", 0)

                result = _robust_json_parse(raw_text)
                print(f"[AI] Success with {model_name} (plain)")
                result['model_used'] = model_name
                return result

            except json.JSONDecodeError as e:
                print(f"[!] JSON parse failed ({model_name}/plain attempt {attempt+1}): {e}")
                if attempt == 0:
                    time.sleep(1)
                    continue
                last_error = f"JSON parse failed ({model_name}/plain): {e}"
                break

            except Exception as e:
                err = str(e)
                print(f"[!] {model_name}/plain error: {err[:120]}")
                if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                    last_error = f"Rate limit: {model_name}"
                    break
                if '404' in err or 'not found' in err.lower():
                    last_error = f"Model unavailable: {model_name}"
                    break
                if attempt == 0:
                    time.sleep(1)
                    continue
                last_error = f"Error ({model_name}/plain): {err[:80]}"
                break

    raise Exception(f"All AI models failed. Last error: {last_error}")


# ---------------------------------------------------------------------------
# Safe fallbacks when ALL models fail
# ---------------------------------------------------------------------------

def _fallback_url_result(url: str) -> dict:
    domain = url.split('/')[2] if '//' in url else url.split('/')[0]
    return {
        "risk_score": 50, "risk_level": "UNKNOWN", "risk_color": "warning",
        "scam_type": "Unable to Analyse", "confidence": "LOW",
        "summary": "AI analysis temporarily unavailable. Treat with caution.",
        "red_flags": ["AI quota exceeded — try again in a few minutes"],
        "legitimate_aspects": [],
        "recommendation": "Wait a few minutes and try again, or verify this URL manually.",
        "what_scammer_wants": "N/A",
        "domain_analysis": {
            "domain": domain, "is_impersonating": "UNKNOWN",
            "impersonating_brand": "N/A", "suspicious_patterns": []
        },
        "ai_powered": False, "model_used": "none"
    }


def _fallback_content_result(check_type: str) -> dict:
    return {
        "risk_score": 50, "risk_level": "UNKNOWN", "risk_color": "warning",
        "scam_type": "Unable to Analyse", "confidence": "LOW",
        "summary": "AI analysis temporarily unavailable. Exercise caution.",
        "red_flags": ["AI quota exceeded — try again in a few minutes"],
        "legitimate_aspects": [],
        "recommendation": "Wait a few minutes and try again. Do not click links or share personal info.",
        "what_scammer_wants": "N/A",
        "ai_powered": False, "model_used": "none"
    }


# ---------------------------------------------------------------------------
# Defaults for required fields (used when truncated response is missing keys)
# ---------------------------------------------------------------------------

_URL_DEFAULTS = {
    "risk_score": 50, "risk_level": "UNKNOWN", "risk_color": "warning",
    "scam_type": "Unable to fully analyse", "confidence": "LOW",
    "summary": "Analysis was partially completed.",
    "red_flags": [], "legitimate_aspects": [],
    "recommendation": "Exercise caution — analysis was incomplete.",
    "what_scammer_wants": "N/A",
    "domain_analysis": {
        "domain": "unknown", "is_impersonating": "UNKNOWN",
        "impersonating_brand": "N/A", "suspicious_patterns": []
    }
}

_CONTENT_DEFAULTS = {
    "risk_score": 50, "risk_level": "UNKNOWN", "risk_color": "warning",
    "scam_type": "Unable to fully analyse", "confidence": "LOW",
    "summary": "Analysis was partially completed.",
    "red_flags": [], "legitimate_aspects": [],
    "recommendation": "Exercise caution — analysis was incomplete.",
    "what_scammer_wants": "N/A"
}

_REPORT_DEFAULTS = {
    "severity": "MEDIUM",
    "scam_category": "Suspicious Activity",
    "summary": "This report describes behavior that should be treated cautiously.",
    "common_patterns": ["Unexpected approach", "Trust-building tactic"],
    "red_flags_identified": ["Suspicious request"],
    "victim_advice": "Stop contact, preserve evidence, and verify through official channels.",
    "prevention_tips": [
        "Do not send money or sensitive information.",
        "Contact the institution through its official number or website."
    ],
    "should_report_to_authorities": "YES",
    "authorities_to_contact": ["FTC", "IC3"],
    "community_impact": "This kind of report helps warn others about the same tactic."
}

_DEFAULT_SENTINELS = {
    "Unable to fully analyse",
    "Analysis was partially completed.",
    "Exercise caution — analysis was incomplete.",
    "unknown",
    "N/A",
}


def _merge_with_defaults(result: dict, defaults: dict) -> dict:
    """Fill in any missing required keys with default values."""
    merged = dict(defaults)
    merged.update(result)
    return merged


def _coerce_list(value):
    """Return a clean list of strings for UI-safe rendering."""
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value in (None, ''):
        return []
    return [str(value).strip()]


def _coerce_int(value, default=50, minimum=0, maximum=100):
    """Convert values like '85%' to bounded integers."""
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        number = int(round(value))
    else:
        match = re.search(r'-?\d+', str(value or ''))
        if not match:
            return default
        number = int(match.group())
    return max(minimum, min(maximum, number))


def normalize_url_input(url: str) -> str:
    """
    Normalize user-entered URLs so partially encoded or scheme-less values
    do not confuse the AI prompt or the UI.
    """
    value = unquote(str(url or '').strip())
    if not value:
        return ''

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', value):
        value = f'https://{value}'

    parts = urlsplit(value)
    if not parts.netloc:
        raise ValueError('Please enter a valid URL, for example https://example.com')

    host = parts.netloc.encode('idna').decode('ascii').lower()
    path = parts.path or '/'
    normalized = f'{parts.scheme.lower()}://{host}{path}'
    if parts.query:
        normalized += f'?{parts.query}'
    if parts.fragment:
        normalized += f'#{parts.fragment}'
    return normalized


def normalize_analysis_result(result: dict, defaults: dict) -> dict:
    """Coerce AI output into a predictable structure for API responses."""
    merged = _merge_with_defaults(result or {}, defaults)
    merged['risk_score'] = _coerce_int(merged.get('risk_score'), default=defaults.get('risk_score', 50))

    raw_level = str(merged.get('risk_level', defaults.get('risk_level', 'UNKNOWN'))).upper().strip()
    if raw_level not in {'LOW', 'MEDIUM', 'HIGH', 'UNKNOWN', 'CRITICAL'}:
        raw_level = defaults.get('risk_level', 'UNKNOWN')
    merged['risk_level'] = raw_level

    raw_confidence = str(merged.get('confidence', defaults.get('confidence', 'LOW'))).upper().strip()
    if raw_confidence not in {'LOW', 'MEDIUM', 'HIGH'}:
        raw_confidence = defaults.get('confidence', 'LOW')
    merged['confidence'] = raw_confidence

    raw_color = str(merged.get('risk_color', defaults.get('risk_color', 'warning'))).lower().strip()
    if raw_color not in {'success', 'warning', 'danger'}:
        raw_color = defaults.get('risk_color', 'warning')
    merged['risk_color'] = raw_color

    for key in ('summary', 'scam_type', 'recommendation', 'what_scammer_wants'):
        merged[key] = str(merged.get(key, defaults.get(key, '')) or defaults.get(key, ''))

    merged['red_flags'] = _coerce_list(merged.get('red_flags'))
    merged['legitimate_aspects'] = _coerce_list(merged.get('legitimate_aspects'))

    if 'domain_analysis' in defaults:
        domain_defaults = defaults.get('domain_analysis', {})
        domain = merged.get('domain_analysis')
        if not isinstance(domain, dict):
            domain = {}
        normalized_domain = dict(domain_defaults)
        normalized_domain.update(domain)
        normalized_domain['domain'] = str(normalized_domain.get('domain', domain_defaults.get('domain', 'unknown')) or domain_defaults.get('domain', 'unknown'))
        flag = str(normalized_domain.get('is_impersonating', domain_defaults.get('is_impersonating', 'UNKNOWN'))).upper().strip()
        if flag not in {'YES', 'NO', 'UNKNOWN'}:
            flag = domain_defaults.get('is_impersonating', 'UNKNOWN')
        normalized_domain['is_impersonating'] = flag
        normalized_domain['impersonating_brand'] = str(normalized_domain.get('impersonating_brand', domain_defaults.get('impersonating_brand', 'N/A')) or domain_defaults.get('impersonating_brand', 'N/A'))
        normalized_domain['suspicious_patterns'] = _coerce_list(normalized_domain.get('suspicious_patterns'))
        merged['domain_analysis'] = normalized_domain

    return merged


def _is_incomplete_result(result: dict, defaults: dict) -> bool:
    """Detect results that mostly contain fallback/default content."""
    if not isinstance(result, dict):
        return True

    for key in ('risk_score', 'risk_level', 'scam_type', 'confidence', 'summary', 'recommendation', 'what_scammer_wants'):
        if key not in result:
            return True

    if defaults is _URL_DEFAULTS and 'domain_analysis' not in result:
        return True

    summary = str(result.get('summary', '')).strip()
    scam_type = str(result.get('scam_type', '')).strip()
    recommendation = str(result.get('recommendation', '')).strip()
    if summary in _DEFAULT_SENTINELS or scam_type in _DEFAULT_SENTINELS or recommendation in _DEFAULT_SENTINELS:
        return True

    if defaults is _URL_DEFAULTS:
        domain = result.get('domain_analysis') or {}
        if not isinstance(domain, dict):
            return True
        if str(domain.get('domain', '')).strip() in {'', 'unknown', 'N/A'}:
            return True

    if defaults is _REPORT_DEFAULTS:
        for key in ('severity', 'scam_category', 'summary', 'victim_advice', 'community_impact'):
            if not str(result.get(key, '')).strip():
                return True

    return False


def _build_retry_prompt(base_prompt: str, defaults: dict) -> str:
    """Ask for a shorter but complete retry when the first response is partial."""
    extra = (
        "Return every requested field. Keep every string under 20 words and every array to 3 items max. "
        "Do not omit keys. If unsure, make the safest reasonable estimate instead of leaving fields blank."
    )
    if defaults is _URL_DEFAULTS:
        extra += " Domain analysis must include domain, is_impersonating, impersonating_brand, and suspicious_patterns."
    return f"{base_prompt}\n\n{extra}"


def _run_analysis_prompt(prompt: str, defaults: dict, max_tokens: int) -> dict:
    """Try the model twice: normal prompt first, then a stricter completion retry."""
    prompts = [prompt, _build_retry_prompt(prompt, defaults)]
    last_result = None

    for idx, candidate in enumerate(prompts):
        result = _call_gemini(candidate, max_tokens=max_tokens)
        normalized = normalize_analysis_result(result, defaults)
        if not _is_incomplete_result(normalized, defaults):
            return normalized
        last_result = normalized
        print(f"[AI] Result incomplete after attempt {idx + 1}; retrying with stricter prompt...")

    return last_result or normalize_analysis_result({}, defaults)


def normalize_report_analysis_result(result: dict) -> dict:
    """Normalize report-analysis output into a complete, UI-friendly structure."""
    merged = dict(_REPORT_DEFAULTS)
    merged.update(result or {})

    severity = str(merged.get('severity', 'MEDIUM')).upper().strip()
    if severity not in {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}:
        severity = 'MEDIUM'
    merged['severity'] = severity

    merged['scam_category'] = str(merged.get('scam_category', _REPORT_DEFAULTS['scam_category']) or _REPORT_DEFAULTS['scam_category'])
    merged['summary'] = str(merged.get('summary', _REPORT_DEFAULTS['summary']) or _REPORT_DEFAULTS['summary'])
    merged['victim_advice'] = str(merged.get('victim_advice', _REPORT_DEFAULTS['victim_advice']) or _REPORT_DEFAULTS['victim_advice'])
    merged['community_impact'] = str(merged.get('community_impact', _REPORT_DEFAULTS['community_impact']) or _REPORT_DEFAULTS['community_impact'])

    merged['common_patterns'] = _coerce_list(merged.get('common_patterns')) or list(_REPORT_DEFAULTS['common_patterns'])
    merged['red_flags_identified'] = _coerce_list(merged.get('red_flags_identified')) or list(_REPORT_DEFAULTS['red_flags_identified'])
    merged['prevention_tips'] = _coerce_list(merged.get('prevention_tips')) or list(_REPORT_DEFAULTS['prevention_tips'])
    merged['authorities_to_contact'] = _coerce_list(merged.get('authorities_to_contact'))

    should_report = str(merged.get('should_report_to_authorities', 'YES')).upper().strip()
    if should_report not in {'YES', 'NO'}:
        should_report = 'YES'
    merged['should_report_to_authorities'] = should_report
    if should_report == 'YES' and not merged['authorities_to_contact']:
        merged['authorities_to_contact'] = list(_REPORT_DEFAULTS['authorities_to_contact'])

    return merged


def _run_report_analysis_prompt(prompt: str, max_tokens: int = 900) -> dict:
    prompts = [prompt, _build_retry_prompt(prompt, _REPORT_DEFAULTS)]
    last_result = None

    for idx, candidate in enumerate(prompts):
        result = _call_gemini(candidate, max_tokens=max_tokens)
        normalized = normalize_report_analysis_result(result)
        if not _is_incomplete_result(normalized, _REPORT_DEFAULTS):
            return normalized
        last_result = normalized
        print(f"[AI] Report result incomplete after attempt {idx + 1}; retrying with stricter prompt...")

    return last_result or normalize_report_analysis_result({})


# ---------------------------------------------------------------------------
# Public analysis functions — SHORT prompts to minimise token usage
# ---------------------------------------------------------------------------

def analyze_with_ai(content: str, check_type: str) -> dict:
    type_label = "email" if check_type == "email" else "message"
    prompt = (
        f'Analyze this {type_label} for scams. '
        f'Return valid JSON with these required keys exactly: '
        f'risk_score, risk_level, risk_color, scam_type, confidence, summary, '
        f'red_flags, legitimate_aspects, recommendation, what_scammer_wants. '
        f'risk_score must be an integer 0-100. risk_level must be LOW, MEDIUM, or HIGH. '
        f'confidence must be LOW, MEDIUM, or HIGH. '
        f'summary must explain the main risk in one sentence. '
        f'red_flags and legitimate_aspects must each be arrays with 1-3 concise items. '
        f'recommendation must be specific and actionable. '
        f'what_scammer_wants must explain the likely goal.\n\n'
        f'Content:\n{content[:4000]}'
    )
    try:
        return _run_analysis_prompt(prompt, _CONTENT_DEFAULTS, max_tokens=900)
    except Exception as e:
        print(f"[!] Content analysis failed: {e}")
        return _fallback_content_result(check_type)


def analyze_report_with_ai(report_data: dict):
    if not GEMINI_AVAILABLE:
        return None
    if not os.environ.get("GEMINI_API_KEY", ""):
        return None

    prompt = (
        f'Analyze this scam report. Return valid JSON with these required keys exactly: '
        f'severity, scam_category, summary, common_patterns, red_flags_identified, victim_advice, '
        f'prevention_tips, should_report_to_authorities, authorities_to_contact, community_impact. '
        f'severity must be LOW, MEDIUM, HIGH, or CRITICAL. '
        f'summary must explain the overall situation in one sentence. '
        f'common_patterns, red_flags_identified, prevention_tips, and authorities_to_contact must be arrays. '
        f'victim_advice and community_impact must be specific and complete.\n\n'
        f'Type: {report_data.get("scam_type","?")} | '
        f'Method: {report_data.get("contact_method","?")} | '
        f'Lost: {report_data.get("lost_money","?")} {report_data.get("amount","")}\n'
        f'Description: {str(report_data.get("description",""))[:1500]}'
    )
    try:
        return _run_report_analysis_prompt(prompt, max_tokens=900)
    except Exception as e:
        print(f"[!] Report analysis failed: {e}")
        return normalize_report_analysis_result({})


def analyze_url_with_ai(url: str) -> dict:
    normalized_url = normalize_url_input(url)
    prompt = (
        f'Analyze this URL for scam/phishing. '
        f'Return valid JSON with these required keys exactly: risk_score, risk_level, risk_color, '
        f'scam_type, confidence, summary, red_flags, legitimate_aspects, recommendation, '
        f'what_scammer_wants, domain_analysis. '
        f'risk_score must be an integer 0-100. risk_level must be LOW, MEDIUM, or HIGH. '
        f'confidence must be LOW, MEDIUM, or HIGH. '
        f'domain_analysis must be an object with: domain, is_impersonating, impersonating_brand, suspicious_patterns. '
        f'is_impersonating must be YES or NO. suspicious_patterns must be an array with 1-3 concise items when suspicious patterns exist.\n\n'
        f'URL: {normalized_url}'
    )
    try:
        normalized = _run_analysis_prompt(prompt, _URL_DEFAULTS, max_tokens=900)
        if normalized.get('domain_analysis', {}).get('domain') in {'unknown', 'N/A', ''}:
            normalized['domain_analysis']['domain'] = urlsplit(normalized_url).netloc
        normalized['analyzed_url'] = normalized_url
        return normalized
    except Exception as e:
        print(f"[!] URL analysis failed: {e}")
        fallback = _fallback_url_result(normalized_url)
        fallback['analyzed_url'] = normalized_url
        return fallback
