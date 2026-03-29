"""Public API endpoints."""
import os
import json
from urllib.parse import urlsplit
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, make_response
from data.checkers import (
    analyze_with_ai,
    analyze_report_with_ai,
    analyze_url_with_ai,
    normalize_analysis_result,
    normalize_url_input,
    _CONTENT_DEFAULTS,
    _URL_DEFAULTS,
    _robust_json_parse,
)
import routes.extensions as ext

api = Blueprint('api', __name__)

# Pakistan Standard Time = UTC+5
_PKT = timezone(timedelta(hours=5))

def _get_pkt_time():
    """Return current time formatted in Pakistan Standard Time."""
    return datetime.now(_PKT).strftime('%d %b %Y, %I:%M %p PKT')

def _to_pkt(ts):
    """Convert any timestamp string to PKT formatted string."""
    if not ts or ts == 'Unknown':
        return ts
    # Already formatted (contains PKT)
    if 'PKT' in str(ts):
        return ts
    try:
        # Try ISO format with timezone info
        from dateutil import parser as dtparser
        dt = dtparser.parse(str(ts))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(_PKT).strftime('%d %b %Y, %I:%M %p PKT')
    except Exception:
        pass
    # Try common formats manually
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try:
            dt = datetime.strptime(str(ts)[:19], fmt[:len(fmt)])
            dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(_PKT).strftime('%d %b %Y, %I:%M %p PKT')
        except Exception:
            continue
    return ts  # Return as-is if all parsing fails

# Absolute path to the reports directory (works regardless of cwd)
_REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')

# Maximum content length accepted for AI analysis (characters)
_MAX_AI_INPUT_LEN = 10_000


def _mark_ai_status(result):
    """Preserve fallback status instead of always claiming Gemini succeeded."""
    ai_ok = bool(result.get('model_used')) and result.get('model_used') != 'none' and result.get('ai_powered', True) is not False
    result['ai_powered'] = ai_ok
    return result


def _normalize_token(value):
    return (value or '').strip().lower().replace('-', '_').replace(' ', '_')


def _difficulty_variants(difficulty):
    normalized = _normalize_token(difficulty)
    variants = [normalized]
    if normalized == 'hard':
        variants.append('difficult')
    elif normalized == 'difficult':
        variants.append('hard')
    return list(dict.fromkeys(v for v in variants if v))


def _scam_type_variants(scam_type):
    normalized = _normalize_token(scam_type)
    variants = [
        scam_type,
        normalized,
        normalized.replace('_', ' '),
        normalized.replace('_', '-'),
    ]
    return list(dict.fromkeys(v for v in variants if v))


def _fetch_quiz_rows(supabase_client, difficulty):
    last_rows = []
    for variant in _difficulty_variants(difficulty):
        db_result = supabase_client.table('quiz_questions').select('*').eq('difficulty', variant).eq('is_active', True).execute()
        rows = db_result.data or []
        if rows:
            return rows
        last_rows = rows
    return last_rows


def _fetch_practice_rows(supabase_client, scam_type):
    last_rows = []
    for variant in _scam_type_variants(scam_type):
        db_result = supabase_client.table('practice_quizzes').select(
            'id, question_text, correct_answer_index, explanation, correct_count, incorrect_count, completion_count'
        ).eq('scam_type', variant).eq('is_active', True).order('display_order').execute()
        rows = db_result.data or []
        if rows:
            return rows
        last_rows = rows
    return last_rows


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def save_report_to_supabase(report):
    """Save report to Supabase cloud database."""
    supabase_client = ext.supabase_client
    if not supabase_client:
        print("[!] Supabase not available")
        return False
    try:
        data = {
            'scam_type': report.get('scam_type'),
            'contact_method': report.get('contact_method'),
            'incident_date': report.get('incident_date'),
            'description': report.get('description'),
            'scammer_contact': report.get('scammer_contact'),
            'lost_money': report.get('lost_money'),
            'amount': report.get('amount'),
            'reporter_email': report.get('reporter_email'),
            'ai_analysis': report.get('ai_analysis'),
            'submitted_at': report.get('submitted_at'),
        }
        result = supabase_client.table('reports').insert(data).execute()
        print(f"[+] Report saved to Supabase: ID {result.data[0]['id'] if result.data else 'unknown'}")
        return True
    except Exception as e:
        print(f"[!] Supabase save failed: {e}")
        return False


def save_report_to_file(report):
    """Save report to local file as backup."""
    try:
        os.makedirs(_REPORTS_DIR, exist_ok=True)
        # FIX: Use PKT time for file naming so filenames match local time
        timestamp = datetime.now(_PKT).strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(_REPORTS_DIR, f"scam_report_{timestamp}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            for key, value in report.items():
                f.write(f"{key}: {value}\n")
        print(f"[+] Report saved locally: {filename}")
        return True
    except Exception as e:
        print(f"[!] Local file save failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@api.route('/api/quiz/questions')
def get_quiz_questions():
    """GET /api/quiz/questions — return quiz questions from database."""
    difficulty = request.args.get('difficulty', 'easy')
    content_service = ext.content_service
    _cache_manager = ext._cache_manager

    if content_service is None:
        return make_response(jsonify({'error': 'Database not available'}), 503)

    cache_key = f"quiz_questions:{difficulty}"
    cache_hit = _cache_manager.get(cache_key) is not None

    try:
        questions = content_service.get_quiz_questions(difficulty=difficulty, use_cache=True)
    except Exception:
        return make_response(jsonify({'error': 'Service unavailable'}), 503)

    resp = make_response(jsonify(questions))
    resp.headers['X-Content-Source'] = 'database'
    resp.headers['X-Cache-Status'] = 'hit' if cache_hit else 'miss'
    return resp


@api.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    supabase_client = ext.supabase_client
    # FIX: use get_json(force=True) + fallback to {} to prevent None crash
    data = request.get_json(force=True, silent=True) or {}
    answers = data.get('answers', [])
    difficulty = data.get('difficulty', 'easy')
    user_name = data.get('name', 'Anonymous')

    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    try:
        db_questions = _fetch_quiz_rows(supabase_client, difficulty)
    except Exception:
        return jsonify({'error': 'Failed to load questions'}), 503

    score = sum(1 for i, ans in enumerate(answers) if i < len(db_questions) and ans == db_questions[i]['correct_answer_index'])
    total = len(db_questions)
    percentage = (score / total * 100) if total > 0 else 0

    results = [
        {
            'correct': (i < len(db_questions)) and (answers[i] == db_questions[i]['correct_answer_index']),
            'explanation': db_questions[i]['explanation'] if i < len(db_questions) else ''
        }
        for i in range(len(answers))
    ]

    try:
        for idx, ans in enumerate(answers):
            if idx < len(db_questions):
                q = db_questions[idx]
                is_correct = ans == q['correct_answer_index']
                field = 'correct_count' if is_correct else 'incorrect_count'
                supabase_client.table('quiz_questions').update({field: (q.get(field, 0) or 0) + 1}).eq('id', q['id']).execute()
    except Exception as _e:
        print(f"[!] Answer stats tracking failed: {_e}")

    return jsonify({
        'score': score,
        'total': total,
        'percentage': percentage,
        'name': user_name,
        'difficulty': difficulty,
        'results': results,
    })


@api.route('/api/practice/submit', methods=['POST'])
def submit_practice_quiz():
    """POST /api/practice/submit — submit practice quiz answers and track completion."""
    supabase_client = ext.supabase_client
    data = request.get_json(force=True, silent=True) or {}
    scam_type = data.get('scam_type', '')
    answers = data.get('answers', [])

    content_service = ext.content_service
    if content_service is None:
        return jsonify({'error': 'Database not available'}), 503

    try:
        questions = content_service.get_practice_quizzes(scam_type=scam_type, use_cache=False)
    except Exception:
        questions = []

    if not questions:
        return jsonify({'error': 'No practice questions found for this scam type'}), 404

    score = sum(1 for i, ans in enumerate(answers) if i < len(questions) and ans == questions[i].get('correct'))
    total = len(questions)
    percentage = (score / total * 100) if total > 0 else 0

    results = [
        {
            'correct': (i < len(questions)) and (answers[i] == questions[i].get('correct')),
            'explanation': questions[i].get('explanation', '') if i < len(questions) else '',
        }
        for i in range(len(answers))
    ]

    if supabase_client is not None:
        try:
            db_questions = _fetch_practice_rows(supabase_client, scam_type)
            for idx, ans in enumerate(answers):
                if idx < len(db_questions):
                    q = db_questions[idx]
                    q_id = q.get('id')
                    if q_id is None:
                        continue
                    is_correct = (idx < len(questions)) and (ans == questions[idx].get('correct'))
                    field = 'correct_count' if is_correct else 'incorrect_count'
                    current = q.get(field, 0) or 0
                    updates = {field: current + 1}
                    if idx == len(answers) - 1:
                        updates['completion_count'] = (q.get('completion_count', 0) or 0) + 1
                    supabase_client.table('practice_quizzes').update(updates).eq('id', q_id).execute()
        except Exception as _e:
            print(f"[!] Practice stats tracking failed: {_e}")

    return jsonify({
        'score': score,
        'total': total,
        'percentage': percentage,
        'scam_type': scam_type,
        'results': results,
    })


@api.route('/api/scams')
def get_scams():
    """GET /api/scams — return all active scam definitions from database."""
    content_service = ext.content_service
    _cache_manager = ext._cache_manager

    if content_service is None:
        return make_response(jsonify({'error': 'Database not available'}), 503)

    cache_key = 'scam_definitions:all'
    cache_hit = _cache_manager.get(cache_key) is not None

    try:
        scams = content_service.get_scam_definitions(use_cache=True)
    except Exception:
        return make_response(jsonify({'error': 'Service unavailable'}), 503)

    resp = make_response(jsonify(scams))
    resp.headers['X-Content-Source'] = 'database'
    resp.headers['X-Cache-Status'] = 'hit' if cache_hit else 'miss'
    return resp


@api.route('/api/scams/<scam_type>')
def get_scam_by_type(scam_type):
    """GET /api/scams/<scam_type> — return a single scam definition from database."""
    content_service = ext.content_service
    supabase_client = ext.supabase_client

    if content_service is None:
        return make_response(jsonify({'error': 'Database not available'}), 503)

    try:
        scam = content_service.get_scam_definitions(scam_type=scam_type, use_cache=True)
    except Exception:
        return make_response(jsonify({'error': 'Service unavailable'}), 503)

    if scam is None:
        return make_response(jsonify({'error': 'Scam type not found'}), 404)

    if supabase_client is not None:
        try:
            row = supabase_client.table('scam_definitions').select('view_count').eq('scam_type', scam_type).execute()
            current_count = (row.data[0].get('view_count') or 0) if row.data else 0
            supabase_client.table('scam_definitions').update(
                {'view_count': current_count + 1}
            ).eq('scam_type', scam_type).execute()
        except Exception:
            pass

    resp = make_response(jsonify(scam))
    resp.headers['X-Content-Source'] = 'database'
    return resp


@api.route('/api/practice/<scam_type>')
def get_practice_questions(scam_type):
    """GET /api/practice/<scam_type> — return practice quiz questions from database."""
    content_service = ext.content_service
    _cache_manager = ext._cache_manager

    if content_service is None:
        return make_response(jsonify({'error': 'Database not available'}), 503)

    cache_key = f"practice_quizzes:{scam_type}"
    cache_hit = _cache_manager.get(cache_key) is not None

    try:
        questions = content_service.get_practice_quizzes(scam_type=scam_type, use_cache=True)
    except Exception:
        return make_response(jsonify({'error': 'Service unavailable'}), 503)

    resp = make_response(jsonify(questions))
    resp.headers['X-Content-Source'] = 'database'
    resp.headers['X-Cache-Status'] = 'hit' if cache_hit else 'miss'
    return resp


@api.route('/api/check', methods=['POST'])
def check_scam():
    data = request.get_json(force=True, silent=True) or {}
    check_type = data.get('type')
    content = data.get('content', '')

    # ... (keep your existing length and type checks) ...

    try:
        if check_type == 'url':
            from data.checkers import analyze_url_with_ai
            raw_result = analyze_url_with_ai(content)
        else:
            raw_result = analyze_with_ai(content, check_type)

        if isinstance(raw_result, str):
            try:
                result = _robust_json_parse(raw_result)
                result.setdefault('model_used', 'raw_ai_response')
            except json.JSONDecodeError:
                return jsonify({
                    'error': 'AI returned invalid formatting',
                    'ai_powered': False,
                    'raw_text': raw_result[:200]
                }), 503
        else:
            result = raw_result

        result = normalize_analysis_result(result, _URL_DEFAULTS if check_type == 'url' else _CONTENT_DEFAULTS)
        _mark_ai_status(result)
        return jsonify(result)

    except Exception as e:
        # This catches the "Unterminated string" error and prevents the 503 crash
        print(f"AI analysis failed: {str(e)}")
        return jsonify({
            'error': 'AI analysis failed',
            'details': "The AI response was cut off or malformed.",
            'ai_powered': False
        }), 503


@api.route('/api/check/url', methods=['POST'])
def check_url():
    """POST /api/check/url — analyze a URL for scam/phishing indicators."""
    data = request.get_json(force=True, silent=True) or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    if len(url) > 2048:
        return jsonify({'error': 'URL too long'}), 413

    try:
        normalized_url = normalize_url_input(url)
        result = analyze_url_with_ai(normalized_url)
        result = normalize_analysis_result(result, _URL_DEFAULTS)
        if result.get('domain_analysis', {}).get('domain') in {'unknown', 'N/A', ''}:
            result['domain_analysis']['domain'] = urlsplit(normalized_url).netloc
        result['analyzed_url'] = result.get('analyzed_url', normalized_url)
        _mark_ai_status(result)
        return jsonify(result)
    except ValueError as e:
        return jsonify({
            'error': 'Invalid URL',
            'details': str(e),
            'ai_powered': False
        }), 400
    except Exception as e:
        error_msg = str(e)
        print(f"URL analysis failed: {error_msg}")
        return jsonify({
            'error': 'AI analysis failed',
            'details': error_msg,
            'ai_powered': False
        }), 503


@api.route('/api/stats')
def get_stats():
    """GET /api/stats — live statistics from Supabase database."""
    supabase_client = ext.supabase_client
    stats = {
        'total_reports': 0,
        'high_risk_reports': 0,
        'total_money_lost': 0,
        'top_scam_type': 'N/A',
        'reports_this_month': 0,
        'most_common_contact_method': 'N/A',
        'database_connected': False
    }

    if not supabase_client:
        return jsonify(stats)

    try:
        result = supabase_client.table('reports').select(
            'scam_type, contact_method, amount, lost_money, submitted_at, ai_analysis'
        ).execute()
        reports = result.data if result.data else []

        stats['database_connected'] = True
        stats['total_reports'] = len(reports)

        if reports:
            stats['high_risk_reports'] = sum(1 for r in reports
                                             if r.get('ai_analysis') and
                                             isinstance(r['ai_analysis'], dict) and
                                             r['ai_analysis'].get('severity') in ['HIGH', 'CRITICAL'])

            total_loss = 0
            for r in reports:
                if r.get('lost_money') == 'yes' and r.get('amount'):
                    try:
                        amount_str = str(r['amount']).replace('$', '').replace(',', '').strip()
                        if amount_str:
                            total_loss += float(amount_str)
                    except Exception:
                        pass
            stats['total_money_lost'] = total_loss

            scam_types = [r.get('scam_type', '') for r in reports if r.get('scam_type')]
            if scam_types:
                stats['top_scam_type'] = max(set(scam_types), key=scam_types.count).replace('_', ' ').title()

            # FIX: Use UTC-aware datetime to match ISO timestamps stored in Supabase
            current_month = datetime.now(timezone.utc).strftime('%Y-%m')
            stats['reports_this_month'] = sum(1 for r in reports
                                              if r.get('submitted_at', '').startswith(current_month))

            contact_methods = [r.get('contact_method', '') for r in reports if r.get('contact_method')]
            if contact_methods:
                stats['most_common_contact_method'] = max(set(contact_methods), key=contact_methods.count).title()

        return jsonify(stats)

    except Exception as e:
        print(f"[!] Error fetching stats: {e}")
        return jsonify(stats)


@api.route('/api/verify', methods=['POST'])
def verify_contact():
    """POST /api/verify — verify if a contact has been reported as a scammer."""
    supabase_client = ext.supabase_client
    data = request.get_json(force=True, silent=True) or {}
    search_query = data.get('query', '').strip()
    search_type = data.get('type', 'auto')

    if not search_query:
        return jsonify({'error': 'No search query provided'}), 400

    if len(search_query) > 500:
        return jsonify({'error': 'Search query too long'}), 413

    if not supabase_client:
        return jsonify({
            'error': 'Database not connected',
            'message': 'Unable to verify at this time. Please try again later.'
        }), 503

    try:
        reports = []
        for variant in _scam_type_variants(search_query):
            result = supabase_client.table('reports').select(
                'scam_type, contact_method, submitted_at, description, lost_money, amount, ai_analysis, scammer_contact'
            ).ilike('scammer_contact', f'%{variant}%').execute()
            reports = result.data if result.data else []
            if reports:
                break

        matching_reports = []
        search_lower = search_query.lower()

        for report in reports:
            scammer_contact = str(report.get('scammer_contact', '')).lower()
            if search_lower in scammer_contact or search_lower == scammer_contact:
                matching_reports.append(report)

        if not matching_reports:
            return jsonify({
                'found': False,
                'message': 'No reports found for this contact.',
                'query': search_query,
                'recommendation': 'This contact has not been reported in our database. However, always exercise caution with unknown contacts.'
            })

        total_reports = len(matching_reports)
        scam_types = [r.get('scam_type', 'Unknown') for r in matching_reports]
        contact_methods = [r.get('contact_method', 'Unknown') for r in matching_reports]

        high_severity = sum(1 for r in matching_reports
                            if r.get('ai_analysis') and
                            isinstance(r['ai_analysis'], dict) and
                            r['ai_analysis'].get('severity') in ['HIGH', 'CRITICAL'])

        most_common_scam = max(set(scam_types), key=scam_types.count) if scam_types else 'Unknown'
        dates = [r.get('submitted_at', '') for r in matching_reports if r.get('submitted_at')]
        most_recent = max(dates) if dates else 'Unknown'

        total_loss = 0
        victims_lost_money = 0
        for r in matching_reports:
            if r.get('lost_money') == 'yes':
                victims_lost_money += 1
                if r.get('amount'):
                    try:
                        amount_str = str(r['amount']).replace('$', '').replace(',', '').strip()
                        if amount_str:
                            total_loss += float(amount_str)
                    except Exception:
                        pass

        sample_descriptions = [
            {
                'date': _to_pkt(r.get('submitted_at', 'Unknown')),
                'scam_type': r.get('scam_type', 'Unknown').replace('_', ' ').title(),
                'description': r.get('description', 'No description')[:200] + ('...' if len(r.get('description', '')) > 200 else ''),
                'contact_method': r.get('contact_method', 'Unknown').title(),
                'lost_money': r.get('lost_money', 'no') == 'yes'
            }
            for r in matching_reports
        ]

        return jsonify({
            'found': True,
            'warning_level': 'HIGH' if high_severity > 0 else 'MEDIUM' if total_reports > 2 else 'LOW',
            'query': search_query,
            'total_reports': total_reports,
            'high_severity_count': high_severity,
            'most_common_scam': most_common_scam.replace('_', ' ').title(),
            'most_recent_report': _to_pkt(most_recent),
            'total_money_lost': total_loss,
            'victims_lost_money': victims_lost_money,
            'contact_methods': list(set(contact_methods)),
            'sample_reports': sample_descriptions,
            'recommendation': f'\u26a0\ufe0f WARNING: This contact has been reported {total_reports} time(s) in our database. Exercise extreme caution and do not share personal or financial information.'
        })

    except Exception as e:
        print(f"[!] Error verifying contact: {e}")
        return jsonify({'error': 'Verification failed', 'message': str(e)}), 500


@api.route('/api/report', methods=['POST'])
def submit_report():
    # FIX: get_json with silent=True prevents AttributeError when body is missing
    data = request.get_json(force=True, silent=True) or {}

    report = {
        'scam_type': data.get('scam_type', 'Not specified'),
        'contact_method': data.get('contact_method', 'Not specified'),
        'incident_date': data.get('incident_date', 'Not specified'),
        'description': data.get('description', 'No description provided'),
        'scammer_contact': data.get('scammer_contact', 'Not provided'),
        'lost_money': data.get('lost_money', 'No'),
        'amount': data.get('amount', 'N/A'),
        'reporter_email': data.get('reporter_email', 'Anonymous'),
        # FIX: Store as UTC ISO string so Supabase treats it as a proper
        # timestamp. _to_pkt() in admin_routes.py converts it to PKT on display.
        'submitted_at': datetime.now(timezone.utc).isoformat()
    }

    ai_analysis = None
    try:
        ai_analysis = analyze_report_with_ai(report)
        if ai_analysis:
            report['ai_analysis'] = ai_analysis
            print(f"AI analysis completed for report: {ai_analysis.get('severity', 'N/A')}")
    except Exception as e:
        print(f"AI report analysis failed: {e}")

    supabase_saved = save_report_to_supabase(report)
    local_saved = save_report_to_file(report)

    response = {
        'success': True,
        'message': 'Your report has been recorded and will help others recognize and avoid this type of scam.'
    }

    if ai_analysis:
        response['ai_analysis'] = ai_analysis
        response['message'] = 'Your report has been analyzed and recorded. Thank you for helping protect the community!'

    if supabase_saved:
        response['stored_in'] = 'cloud'
    elif local_saved:
        response['stored_in'] = 'local'

    return jsonify(response)
