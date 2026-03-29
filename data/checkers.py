import re
import json
import os
import time
from urllib.parse import unquote, urlsplit
from dotenv import load_dotenv

# Force the import - handles Render environment constraints
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()

# ---------------------------------------------------------------------------
# Truncated JSON recovery
# Handles the case where the model cuts off mid-response due to rate limits
# ---------------------------------------------------------------------------

def _recover_truncated_json(text: str) -> dict:
    """
    Try to salvage a truncated JSON response by extracting complete
    top-level key-value pairs before the cutoff.
    """
    start = text.find('{')
    if start == -1:
        raise ValueError("No opening brace found")

    partial = text[start:]
    recovered = {}

    # Match string values: "key": "value"
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

    # Match array values: "key": ["item1", "item2"]
    for m in re.finditer(r'"([^"]+)"\s*:\s*\[([^\]]*)\]', partial):
        key = m.group(1)
        if key not in recovered:
            items = re.findall(r'"([^"]*)"', m.group(2))
            recovered[key] = items

    # Match nested object values (like domain_analysis)
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

def _robust_json_parse(raw_text: str) -> dict:
    """Parse JSON from AI output with multiple fallback strategies."""
    text = raw_text.strip()

    def _clean(s):
        s = re.sub(r'^```[a-zA-Z]*\r?\n?', '', s, flags=re.MULTILINE)
        s = re.sub(r'\r?\n?```\s*$', '', s, flags=re.MULTILINE)
        s = s.strip()
        brace_match = re.search(r'\{[\s\S]*\}', s)
        if brace_match:
            s = brace_match.group()
        s = re.sub(r'//[^\n"]*(?=\n|$)', '', s)
        s = re.sub(r'/\*[\s\S]*?\*/', '', s)
        s = re.sub(r',\s*([}\]])', r'\1', s)
        s = re.sub(r'\bNone\b', 'null', s)
        s = re.sub(r'\bTrue\b', 'true', s)
        s = re.sub(r'\bFalse\b', 'false', s)
        return s.strip()

    # Try normal parse
    try:
        return json.loads(text)
    except:
        try:
            return json.loads(_clean(text))
        except:
            pass

    # Try truncated recovery
    try:
        return _recover_truncated_json(text)
    except:
        raise json.JSONDecodeError("Failed to parse or recover JSON", text, 0)

# ---------------------------------------------------------------------------
# AI Model Configuration
# ---------------------------------------------------------------------------

_SYSTEM_INSTRUCTION = (
    "You are the ScamGuard JSON API. Output ONLY a valid JSON object. "
    "No conversational text. No markdown fences. Start with { and end with }. "
    "Be concise: keep strings under 20 words."
)

_MODELS = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']

def _call_gemini(prompt: str, max_tokens: int = 900) -> dict:
    if not GEMINI_AVAILABLE:
        raise Exception("Google GenAI not installed")

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise Exception("GEMINI_API_KEY missing")

    client = genai.Client(api_key=api_key)
    
    for model_name in _MODELS:
        try:
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
            if not raw_text: continue
            
            result = _robust_json_parse(raw_text)
            result['model_used'] = model_name
            return result
        except Exception as e:
            print(f"[AI] Model {model_name} failed: {e}")
            continue
            
    raise Exception("All AI models failed or rate-limited.")

# ---------------------------------------------------------------------------
# Defaults & Normalization
# ---------------------------------------------------------------------------

_URL_DEFAULTS = {
    "risk_score": 50, "risk_level": "UNKNOWN", "risk_color": "warning",
    "scam_type": "Analysis Incomplete", "confidence": "LOW",
    "summary": "AI was unable to reach a full conclusion.",
    "red_flags": [], "legitimate_aspects": [],
    "recommendation": "Treat this URL with caution.",
    "what_scammer_wants": "Unknown",
    "domain_analysis": {"domain": "unknown", "is_impersonating": "UNKNOWN", "impersonating_brand": "N/A", "suspicious_patterns": []}
}

_CONTENT_DEFAULTS = {
    "risk_score": 50, "risk_level": "UNKNOWN", "risk_color": "warning",
    "scam_type": "Analysis Incomplete", "confidence": "LOW",
    "summary": "The analysis was interrupted mid-way.",
    "red_flags": [], "legitimate_aspects": [],
    "recommendation": "Be wary of sharing info with this sender.",
    "what_scammer_wants": "Unknown"
}

def normalize_url_input(url: str) -> str:
    value = unquote(str(url or '').strip())
    if not value: return ''
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', value):
        value = f'https://{value}'
    parts = urlsplit(value)
    host = parts.netloc.encode('idna').decode('ascii').lower()
    return f'{parts.scheme.lower()}://{host}{parts.path or "/"}'

def _coerce_int(v, default=50):
    try:
        if isinstance(v, (int, float)): return int(v)
        return int(re.search(r'\d+', str(v)).group())
    except: return default

def _coerce_list(v):
    return [str(i) for i in v] if isinstance(v, list) else []

def normalize_analysis_result(result: dict, defaults: dict) -> dict:
    merged = dict(defaults)
    merged.update(result or {})
    merged['risk_score'] = _coerce_int(merged.get('risk_score'), defaults.get('risk_score'))
    merged['red_flags'] = _coerce_list(merged.get('red_flags'))
    merged['legitimate_aspects'] = _coerce_list(merged.get('legitimate_aspects'))
    
    if 'domain_analysis' in defaults:
        d_merged = dict(defaults['domain_analysis'])
        d_merged.update(merged.get('domain_analysis') or {})
        d_merged['suspicious_patterns'] = _coerce_list(d_merged.get('suspicious_patterns'))
        merged['domain_analysis'] = d_merged
    return merged

# ---------------------------------------------------------------------------
# Public API Functions
# ---------------------------------------------------------------------------

def analyze_url_with_ai(url: str) -> dict:
    normalized_url = normalize_url_input(url)
    prompt = f"Analyze URL for phishing: {normalized_url}. Return JSON: risk_score, risk_level, risk_color, scam_type, confidence, summary, red_flags, legitimate_aspects, recommendation, what_scammer_wants, domain_analysis(obj: domain, is_impersonating, impersonating_brand, suspicious_patterns)."
    try:
        raw_res = _call_gemini(prompt)
        res = normalize_analysis_result(raw_res, _URL_DEFAULTS)
        res['analyzed_url'] = normalized_url
        return res
    except:
        return _URL_DEFAULTS

def analyze_with_ai(content: str, check_type: str) -> dict:
    prompt = f"Analyze this {check_type} for scams: {content[:3000]}. Return JSON: risk_score, risk_level, risk_color, scam_type, confidence, summary, red_flags, legitimate_aspects, recommendation, what_scammer_wants."
    try:
        raw_res = _call_gemini(prompt)
        return normalize_analysis_result(raw_res, _CONTENT_DEFAULTS)
    except:
        return _CONTENT_DEFAULTS

def analyze_report_with_ai(report_data: dict):
    desc = str(report_data.get("description",""))[:1000]
    prompt = f"Analyze Scam Report. Category: {report_data.get('scam_type')}. Desc: {desc}. Return JSON: severity, scam_category, summary, common_patterns, red_flags_identified, victim_advice, prevention_tips, should_report_to_authorities(YES/NO), authorities_to_contact, community_impact."
    try:
        return _call_gemini(prompt)
    except:
        return {"summary": "Analysis failed."}
