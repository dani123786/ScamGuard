import re
import json
import os
import time

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai package not installed. AI features will use fallback mode.")


# ---------------------------------------------------------------------------
# Shared Gemini call helper — single source of truth for model fallback logic
# ---------------------------------------------------------------------------

_MODELS = [
    'models/gemini-1.5-flash',
    'models/gemini-2.0-flash',
    'models/gemini-2.5-flash',
]

def _call_gemini(prompt: str, max_tokens: int = 800) -> dict:
    """
    Call the Gemini API with automatic model fallback.

    Tries each model in _MODELS order. For 429/503 errors it moves to the
    next model immediately (or after a brief wait for 503). Returns a parsed
    JSON dict on success. Raises Exception if all models are exhausted.
    """
    if not GEMINI_AVAILABLE:
        raise Exception("Google GenAI package not installed")

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key or len(api_key) < 20:
        raise Exception("GEMINI_API_KEY not set or appears invalid")

    # Create the client once — reused across all retries
    client = genai.Client(api_key=api_key)

    last_error = None

    for model_name in _MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=max_tokens,
                        response_mime_type='application/json',
                    ),
                )

                raw_text = response.text.strip()

                # Strip markdown code fences if present
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```[a-z]*\n?", "", raw_text)
                    raw_text = re.sub(r"\n?```$", "", raw_text)

                result = json.loads(raw_text.strip())
                result['model_used'] = model_name.replace('models/', '')
                return result

            except json.JSONDecodeError as e:
                if attempt == 0:
                    continue  # Retry same model once
                last_error = f"Invalid JSON from {model_name}: {e}"
                break  # Try next model

            except Exception as e:
                err = str(e)

                if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                    last_error = f"Rate limit on {model_name}"
                    break  # Move to next model immediately

                if '503' in err or 'high demand' in err.lower():
                    if attempt == 0:
                        time.sleep(2)
                        continue
                    last_error = f"Service unavailable for {model_name}"
                    break

                last_error = f"Error with {model_name}: {e}"
                break  # Try next model

    raise Exception(f"All AI models failed. Last error: {last_error}")


# ---------------------------------------------------------------------------
# Public analysis functions
# ---------------------------------------------------------------------------

def analyze_with_ai(content: str, check_type: str) -> dict:
    """
    Analyze email/message content for scam indicators using Gemini AI.

    Returns a structured dict with risk_score, risk_level, scam_type,
    red_flags, recommendation, and more.
    """
    type_label = "email" if check_type == "email" else "message"

    prompt = f"""Analyze this {type_label} for scams and fraud. Return valid JSON only.

Content: {content}

Required JSON format:
{{
  "risk_score": 0-100,
  "risk_level": "LOW/MEDIUM/HIGH",
  "risk_color": "success/warning/danger",
  "scam_type": "type or None Detected",
  "confidence": "LOW/MEDIUM/HIGH",
  "summary": "one sentence summary",
  "red_flags": ["flag1", "flag2"],
  "legitimate_aspects": ["aspect1"],
  "recommendation": "what user should do",
  "what_scammer_wants": "goal or N/A"
}}

Scoring: 0-24=LOW, 25-54=MEDIUM, 55-100=HIGH. Keep text short."""

    return _call_gemini(prompt, max_tokens=800)


def analyze_report_with_ai(report_data: dict):
    """
    Analyze a submitted scam report and return insights.

    Returns None (instead of raising) when analysis is unavailable, so
    reports can still be saved without AI enrichment.
    """
    if not GEMINI_AVAILABLE:
        return None

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None

    prompt = f"""Analyze this scam report and provide insights. Return valid JSON only.

Report:
- Type: {report_data.get('scam_type', 'Not specified')}
- Method: {report_data.get('contact_method', 'Not specified')}
- Date: {report_data.get('incident_date', 'Not specified')}
- Description: {report_data.get('description', 'No description')}
- Contact: {report_data.get('scammer_contact', 'Not provided')}
- Money Lost: {report_data.get('lost_money', 'No')} - {report_data.get('amount', 'N/A')}

Required JSON format:
{{
  "severity": "LOW/MEDIUM/HIGH/CRITICAL",
  "scam_category": "category",
  "common_patterns": ["pattern1", "pattern2"],
  "red_flags_identified": ["flag1", "flag2"],
  "victim_advice": "advice",
  "prevention_tips": ["tip1", "tip2"],
  "should_report_to_authorities": "YES/NO",
  "authorities_to_contact": ["authority1"],
  "community_impact": "impact statement"
}}

Keep text short."""

    try:
        return _call_gemini(prompt, max_tokens=600)
    except Exception as e:
        print(f"AI report analysis failed: {e}")
        return None


def analyze_url_with_ai(url: str) -> dict:
    """
    Analyze a URL for scam/phishing indicators using Gemini AI.

    Returns a structured dict with risk_score, risk_level, domain_analysis,
    red_flags, and recommendation.
    """
    prompt = f"""Analyze this URL for scam, phishing, or malicious indicators. Return valid JSON only.

URL: {url}

Analyze the following aspects:
- Domain name (typosquatting, fake brands, suspicious TLDs)
- URL structure (excessive subdomains, random strings, IP addresses)
- Known scam patterns (fake login pages, prize claims, crypto scams)
- Brand impersonation (paypal, amazon, microsoft, google, banks etc)
- Overall trustworthiness

Required JSON format:
{{
  "risk_score": 0-100,
  "risk_level": "LOW/MEDIUM/HIGH",
  "risk_color": "success/warning/danger",
  "scam_type": "type or None Detected",
  "confidence": "LOW/MEDIUM/HIGH",
  "summary": "one sentence summary of what this URL appears to be",
  "red_flags": ["flag1", "flag2"],
  "legitimate_aspects": ["aspect1"],
  "recommendation": "what user should do",
  "what_scammer_wants": "goal or N/A",
  "domain_analysis": {{
    "domain": "extracted domain",
    "is_impersonating": "YES/NO",
    "impersonating_brand": "brand name or N/A",
    "suspicious_patterns": ["pattern1"]
  }}
}}

Scoring: 0-24=LOW, 25-54=MEDIUM, 55-100=HIGH."""

    return _call_gemini(prompt, max_tokens=800)
