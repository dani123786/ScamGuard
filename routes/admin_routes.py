"""Admin content management API routes."""
import json
from functools import wraps
from flask import Blueprint, request, jsonify, render_template, redirect
import routes.extensions as ext

admin_content = Blueprint('admin_content', __name__)


# Lazy auth decorators — delegate to whatever ext.require_auth/require_role
# point to at request time (set during app init).
def _auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return ext.require_auth(f)(*args, **kwargs)
    return wrapper


def _role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return ext.require_role(*roles)(f)(*args, **kwargs)
        return wrapper
    return decorator


def _parse_ai_analysis(r):
    """
    FIX: Supabase may return ai_analysis as a JSON string instead of a dict
    (depending on how the column type is configured). Parse it so Jinja2
    template can call .get() on it correctly.
    """
    raw = r.get('ai_analysis')
    if raw is None:
        return
    if isinstance(raw, str):
        try:
            r['ai_analysis'] = json.loads(raw)
        except (ValueError, TypeError):
            r['ai_analysis'] = None
    # If it's already a dict, leave it as-is


# ---------------------------------------------------------------------------
# Reports dashboard
# ---------------------------------------------------------------------------

@admin_content.route('/admin/reports')
def admin_reports():
    """Admin dashboard to view all submitted reports."""
    if ext._AUTH_AVAILABLE:
        if ext._auth_get_current_user() is None:
            return redirect('/admin/login')

    supabase_client = ext.supabase_client
    if not supabase_client:
        return render_template('admin.html',
                               reports=[], total_reports=0, high_risk=0,
                               total_loss=0, top_scam_type='N/A',
                               error='Database not connected. Please configure Supabase.')
    try:
        result = supabase_client.table('reports').select('*').order('submitted_at', desc=True).execute()
        reports = result.data if result.data else []

        from routes.api import _to_pkt
        for r in reports:
            # FIX: Convert ai_analysis JSON string → dict so template .get() works
            _parse_ai_analysis(r)
            # FIX: Convert UTC timestamp → PKT for display in admin portal
            if r.get('submitted_at'):
                r['submitted_at'] = _to_pkt(r['submitted_at'])

        total_reports = len(reports)
        high_risk = sum(1 for r in reports
                        if isinstance(r.get('ai_analysis'), dict) and
                        r['ai_analysis'].get('severity') in ['HIGH', 'CRITICAL'])
        total_loss = 0
        for r in reports:
            if r.get('lost_money') == 'yes' and r.get('amount'):
                try:
                    amount_str = str(r['amount']).replace('$', '').replace(',', '').strip()
                    total_loss += float(amount_str)
                except Exception:
                    pass
        scam_types = [r.get('scam_type', '') for r in reports if r.get('scam_type')]
        top_scam_type = max(set(scam_types), key=scam_types.count) if scam_types else 'N/A'
        return render_template('admin.html',
                               reports=reports, total_reports=total_reports,
                               high_risk=high_risk, total_loss=total_loss,
                               top_scam_type=top_scam_type.replace('_', ' ').title(),
                               error=None)
    except Exception as e:
        return render_template('admin.html',
                               reports=[], total_reports=0, high_risk=0,
                               total_loss=0, top_scam_type='N/A', error=str(e))


# ---------------------------------------------------------------------------
# Quiz Questions
# ---------------------------------------------------------------------------

@admin_content.route('/admin/quiz-questions', methods=['GET'])
@_auth
def admin_list_quiz_questions():
    """GET /admin/quiz-questions — list all quiz questions with optional filters."""
    supabase_client = ext.supabase_client
    search = request.args.get('search', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    per_page = 20

    if supabase_client is None:
        from data.quiz_questions import QUIZ_QUESTIONS
        all_questions = []
        for diff, qs in QUIZ_QUESTIONS.items():
            for i, q in enumerate(qs):
                all_questions.append({
                    'id': f'{diff}_{i}',
                    'question_text': q.get('question', ''),
                    'options': q.get('options', []),
                    'correct_answer_index': q.get('correct', 0),
                    'explanation': q.get('explanation', ''),
                    'difficulty': diff,
                    'is_active': True,
                    'created_at': None,
                    'updated_at': None,
                })
        if search:
            all_questions = [q for q in all_questions if search.lower() in q['question_text'].lower()]
        if difficulty:
            all_questions = [q for q in all_questions if q['difficulty'] == difficulty]
        total = len(all_questions)
        pages = max(1, (total + per_page - 1) // per_page)
        start = (page - 1) * per_page
        return jsonify({'questions': all_questions[start:start + per_page],
                        'total': total, 'page': page, 'pages': pages})

    try:
        query = supabase_client.table('quiz_questions').select('*')
        if difficulty:
            query = query.eq('difficulty', difficulty)
        result = query.execute()
        questions = result.data or []
        if search:
            questions = [q for q in questions if search.lower() in (q.get('question_text') or '').lower()]
        out = []
        for q in questions:
            opts = q.get('options') or [q.get('option_1', ''), q.get('option_2', ''),
                                         q.get('option_3', ''), q.get('option_4', '')]
            out.append({
                'id': q.get('id'),
                'question_text': q.get('question_text', ''),
                'options': opts,
                'correct_answer_index': q.get('correct_answer_index', 0),
                'explanation': q.get('explanation', ''),
                'difficulty': q.get('difficulty', ''),
                'is_active': q.get('is_active', True),
                'created_at': q.get('created_at'),
                'updated_at': q.get('updated_at'),
            })
        total = len(out)
        pages = max(1, (total + per_page - 1) // per_page)
        start = (page - 1) * per_page
        return jsonify({'questions': out[start:start + per_page],
                        'total': total, 'page': page, 'pages': pages})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/quiz-questions', methods=['POST'])
@_auth
@_role('editor', 'admin')
def admin_create_quiz_question():
    """POST /admin/quiz-questions — create a new quiz question."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    data = request.get_json(force=True) or {}
    if ext._content_validator:
        valid, errors = ext._content_validator.validate_quiz_question(data)
        if not valid:
            return jsonify({'errors': errors}), 400

    options = data.get('options', [])
    record = {
        'question_text': data.get('question_text', ''),
        'option_1': options[0] if len(options) > 0 else '',
        'option_2': options[1] if len(options) > 1 else '',
        'option_3': options[2] if len(options) > 2 else '',
        'option_4': options[3] if len(options) > 3 else '',
        'correct_answer_index': data.get('correct_answer_index'),
        'explanation': data.get('explanation', ''),
        'difficulty': data.get('difficulty', ''),
        'is_active': True,
    }
    try:
        result = supabase_client.table('quiz_questions').insert(record).execute()
        created = result.data[0] if result.data else record
        if ext._audit_logger:
            ext._audit_logger.log_create('quiz_questions', created.get('id'), created)
        ext._invalidate_quiz_cache()
        return jsonify(created), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/quiz-questions/<int:question_id>', methods=['PUT'])
@_auth
@_role('editor', 'admin')
def admin_update_quiz_question(question_id):
    """PUT /admin/quiz-questions/<id> — update an existing quiz question."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    try:
        existing_result = supabase_client.table('quiz_questions').select('*').eq('id', question_id).execute()
        if not existing_result.data:
            return jsonify({'error': 'Not found'}), 404
        old_record = existing_result.data[0]
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    data = request.get_json(force=True) or {}
    if ext._content_validator:
        merged = {**old_record, **data}
        valid, errors = ext._content_validator.validate_quiz_question(merged)
        if not valid:
            return jsonify({'errors': errors}), 400

    updates = {}
    if 'question_text' in data:
        updates['question_text'] = data['question_text']
    if 'options' in data:
        opts = data['options']
        updates['option_1'] = opts[0] if len(opts) > 0 else ''
        updates['option_2'] = opts[1] if len(opts) > 1 else ''
        updates['option_3'] = opts[2] if len(opts) > 2 else ''
        updates['option_4'] = opts[3] if len(opts) > 3 else ''
    if 'correct_answer_index' in data:
        updates['correct_answer_index'] = data['correct_answer_index']
    if 'explanation' in data:
        updates['explanation'] = data['explanation']
    if 'difficulty' in data:
        updates['difficulty'] = data['difficulty']

    try:
        result = supabase_client.table('quiz_questions').update(updates).eq('id', question_id).execute()
        updated = result.data[0] if result.data else {**old_record, **updates}
        if ext._audit_logger:
            ext._audit_logger.log_update('quiz_questions', question_id, old_record, updated)
        ext._invalidate_quiz_cache()
        return jsonify(updated)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/quiz-questions/<int:question_id>', methods=['DELETE'])
@_auth
@_role('editor', 'admin')
def admin_delete_quiz_question(question_id):
    """DELETE /admin/quiz-questions/<id> — soft delete a quiz question."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    try:
        existing_result = supabase_client.table('quiz_questions').select('*').eq('id', question_id).execute()
        if not existing_result.data:
            return jsonify({'error': 'Not found'}), 404
        old_record = existing_result.data[0]
        supabase_client.table('quiz_questions').update({'is_active': False}).eq('id', question_id).execute()
        if ext._audit_logger:
            ext._audit_logger.log_delete('quiz_questions', question_id, old_record)
        ext._invalidate_quiz_cache()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/quiz-questions/bulk', methods=['POST'])
@_auth
@_role('editor', 'admin')
def admin_bulk_quiz_questions():
    """POST /admin/quiz-questions/bulk — bulk delete or change difficulty."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    data = request.get_json(force=True) or {}
    action = data.get('action')
    ids = data.get('ids', [])
    difficulty = data.get('difficulty')

    if action not in ('delete', 'change_difficulty'):
        return jsonify({'error': 'action must be "delete" or "change_difficulty"'}), 400
    if not ids:
        return jsonify({'updated': 0})

    updated = 0
    try:
        for qid in ids:
            existing_result = supabase_client.table('quiz_questions').select('*').eq('id', qid).execute()
            if not existing_result.data:
                continue
            old_record = existing_result.data[0]
            if action == 'delete':
                supabase_client.table('quiz_questions').update({'is_active': False}).eq('id', qid).execute()
                if ext._audit_logger:
                    ext._audit_logger.log_delete('quiz_questions', qid, old_record)
            elif action == 'change_difficulty':
                if difficulty not in ('easy', 'medium', 'difficult'):
                    return jsonify({'error': 'difficulty must be easy, medium, or difficult'}), 400
                supabase_client.table('quiz_questions').update({'difficulty': difficulty}).eq('id', qid).execute()
                if ext._audit_logger:
                    ext._audit_logger.log_update('quiz_questions', qid, old_record, {**old_record, 'difficulty': difficulty})
            updated += 1
        ext._invalidate_quiz_cache()
        return jsonify({'updated': updated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Scam Definitions
# ---------------------------------------------------------------------------

@admin_content.route('/admin/scam-definitions', methods=['GET'])
@_auth
def admin_list_scam_definitions():
    """GET /admin/scam-definitions — list all scam definitions."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        from data.scams import SCAMS_DATA
        scams = []
        for scam_type, s in SCAMS_DATA.items():
            scams.append({
                'id': None, 'scam_type': scam_type,
                'title': s.get('title', ''), 'icon': s.get('icon', ''),
                'color': s.get('color', ''), 'description': s.get('description', ''),
                'warning_signs': s.get('warning_signs', []),
                'prevention_tips': s.get('prevention', []),
                'is_active': True, 'view_count': 0,
            })
        return jsonify({'scams': scams})

    try:
        result = supabase_client.table('scam_definitions').select('*').execute()
        scams = []
        for s in (result.data or []):
            scams.append({
                'id': s.get('id'), 'scam_type': s.get('scam_type', ''),
                'title': s.get('title', ''), 'icon': s.get('icon', ''),
                'color': s.get('color', ''), 'description': s.get('description', ''),
                'warning_signs': s.get('warning_signs', []),
                'prevention_tips': s.get('prevention_tips', []),
                'is_active': s.get('is_active', True),
                'view_count': s.get('view_count', 0),
            })
        return jsonify({'scams': scams})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/scam-definitions', methods=['POST'])
@_auth
@_role('editor', 'admin')
def admin_create_scam_definition():
    """POST /admin/scam-definitions — create a new scam definition."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    data = request.get_json(force=True) or {}
    if ext._content_validator:
        valid, errors = ext._content_validator.validate_scam_definition(data)
        if not valid:
            return jsonify({'errors': errors}), 400

    scam_type = data.get('scam_type', '')
    try:
        existing = supabase_client.table('scam_definitions').select('id').eq('scam_type', scam_type).execute()
        if existing.data:
            return jsonify({'errors': [f'scam_type "{scam_type}" already exists']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    record = {
        'scam_type': scam_type,
        'title': data.get('title', ''), 'icon': data.get('icon', ''),
        'color': data.get('color', ''), 'description': data.get('description', ''),
        'warning_signs': data.get('warning_signs', []),
        'prevention_tips': data.get('prevention_tips', []),
        'is_active': True,
    }
    try:
        result = supabase_client.table('scam_definitions').insert(record).execute()
        created = result.data[0] if result.data else record
        if ext._audit_logger:
            ext._audit_logger.log_create('scam_definitions', created.get('id'), created)
        ext._invalidate_scam_cache(scam_type)
        return jsonify(created), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/scam-definitions/<int:scam_id>', methods=['PUT'])
@_auth
@_role('editor', 'admin')
def admin_update_scam_definition(scam_id):
    """PUT /admin/scam-definitions/<id> — update a scam definition."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    try:
        existing_result = supabase_client.table('scam_definitions').select('*').eq('id', scam_id).execute()
        if not existing_result.data:
            return jsonify({'error': 'Not found'}), 404
        old_record = existing_result.data[0]
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    data = request.get_json(force=True) or {}
    if ext._content_validator:
        merged = {**old_record, **data}
        valid, errors = ext._content_validator.validate_scam_definition(merged)
        if not valid:
            return jsonify({'errors': errors}), 400

    updates = {k: data[k] for k in ('title', 'icon', 'color', 'description', 'warning_signs', 'prevention_tips') if k in data}
    try:
        result = supabase_client.table('scam_definitions').update(updates).eq('id', scam_id).execute()
        updated = result.data[0] if result.data else {**old_record, **updates}
        if ext._audit_logger:
            ext._audit_logger.log_update('scam_definitions', scam_id, old_record, updated)
        ext._invalidate_scam_cache(old_record.get('scam_type'))
        return jsonify(updated)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/scam-definitions/<int:scam_id>', methods=['DELETE'])
@_auth
@_role('editor', 'admin')
def admin_delete_scam_definition(scam_id):
    """DELETE /admin/scam-definitions/<id> — soft delete a scam definition."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    try:
        existing_result = supabase_client.table('scam_definitions').select('*').eq('id', scam_id).execute()
        if not existing_result.data:
            return jsonify({'error': 'Not found'}), 404
        old_record = existing_result.data[0]
        scam_type = old_record.get('scam_type', '')

        pq_result = supabase_client.table('practice_quizzes').select('id').eq('scam_type', scam_type).eq('is_active', True).execute()
        had_practice_quizzes = bool(pq_result.data)

        supabase_client.table('scam_definitions').update({'is_active': False}).eq('id', scam_id).execute()
        if ext._audit_logger:
            ext._audit_logger.log_delete('scam_definitions', scam_id, old_record)
        ext._invalidate_scam_cache(scam_type)
        return jsonify({'success': True, 'had_practice_quizzes': had_practice_quizzes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Practice Quizzes
# ---------------------------------------------------------------------------

@admin_content.route('/admin/practice-quizzes', methods=['GET'])
@_auth
def admin_list_practice_quizzes():
    """GET /admin/practice-quizzes — list practice quizzes grouped by scam_type."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        from data.practice_quizzes import PRACTICE_QUIZZES
        groups = {}
        for scam_type, qs in PRACTICE_QUIZZES.items():
            groups[scam_type] = {'count': len(qs), 'questions': qs}
        return jsonify({'groups': groups})

    try:
        result = supabase_client.table('practice_quizzes').select('*').order('display_order').execute()
        groups = {}
        for q in (result.data or []):
            st = q.get('scam_type', '')
            if st not in groups:
                groups[st] = {'count': 0, 'questions': []}
            groups[st]['questions'].append(q)
            groups[st]['count'] += 1
        return jsonify({'groups': groups})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/practice-quizzes', methods=['POST'])
@_auth
@_role('editor', 'admin')
def admin_create_practice_quiz():
    """POST /admin/practice-quizzes — create a new practice quiz question."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    data = request.get_json(force=True) or {}
    if ext._content_validator:
        valid, errors = ext._content_validator.validate_practice_quiz(data)
        if not valid:
            return jsonify({'errors': errors}), 400

    scam_type = data.get('scam_type', '')
    try:
        sd_result = supabase_client.table('scam_definitions').select('id').eq('scam_type', scam_type).eq('is_active', True).execute()
        if not sd_result.data:
            return jsonify({'errors': [f'scam_type "{scam_type}" not found in active scam definitions']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    options = data.get('options', [])
    record = {
        'scam_type': scam_type,
        'question_text': data.get('question_text', ''),
        'option_1': options[0] if len(options) > 0 else '',
        'option_2': options[1] if len(options) > 1 else '',
        'option_3': options[2] if len(options) > 2 else '',
        'option_4': options[3] if len(options) > 3 else '',
        'correct_answer_index': data.get('correct_answer_index'),
        'explanation': data.get('explanation', ''),
        'is_active': True,
    }
    if data.get('display_order') is not None:
        record['display_order'] = data['display_order']

    try:
        result = supabase_client.table('practice_quizzes').insert(record).execute()
        created = result.data[0] if result.data else record
        if ext._audit_logger:
            ext._audit_logger.log_create('practice_quizzes', created.get('id'), created)
        ext._invalidate_practice_cache(scam_type)
        return jsonify(created), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/practice-quizzes/<int:quiz_id>', methods=['PUT'])
@_auth
@_role('editor', 'admin')
def admin_update_practice_quiz(quiz_id):
    """PUT /admin/practice-quizzes/<id> — update a practice quiz question."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    try:
        existing_result = supabase_client.table('practice_quizzes').select('*').eq('id', quiz_id).execute()
        if not existing_result.data:
            return jsonify({'error': 'Not found'}), 404
        old_record = existing_result.data[0]
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    data = request.get_json(force=True) or {}
    if ext._content_validator:
        merged = {**old_record, **data}
        valid, errors = ext._content_validator.validate_practice_quiz(merged)
        if not valid:
            return jsonify({'errors': errors}), 400

    updates = {}
    if 'question_text' in data:
        updates['question_text'] = data['question_text']
    if 'options' in data:
        opts = data['options']
        updates['option_1'] = opts[0] if len(opts) > 0 else ''
        updates['option_2'] = opts[1] if len(opts) > 1 else ''
        updates['option_3'] = opts[2] if len(opts) > 2 else ''
        updates['option_4'] = opts[3] if len(opts) > 3 else ''
    if 'correct_answer_index' in data:
        updates['correct_answer_index'] = data['correct_answer_index']
    if 'explanation' in data:
        updates['explanation'] = data['explanation']
    if 'display_order' in data:
        updates['display_order'] = data['display_order']

    try:
        result = supabase_client.table('practice_quizzes').update(updates).eq('id', quiz_id).execute()
        updated = result.data[0] if result.data else {**old_record, **updates}
        if ext._audit_logger:
            ext._audit_logger.log_update('practice_quizzes', quiz_id, old_record, updated)
        ext._invalidate_practice_cache(old_record.get('scam_type'))
        return jsonify(updated)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/practice-quizzes/<int:quiz_id>', methods=['DELETE'])
@_auth
@_role('editor', 'admin')
def admin_delete_practice_quiz(quiz_id):
    """DELETE /admin/practice-quizzes/<id> — soft delete a practice quiz question."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    try:
        existing_result = supabase_client.table('practice_quizzes').select('*').eq('id', quiz_id).execute()
        if not existing_result.data:
            return jsonify({'error': 'Not found'}), 404
        old_record = existing_result.data[0]
        supabase_client.table('practice_quizzes').update({'is_active': False}).eq('id', quiz_id).execute()
        if ext._audit_logger:
            ext._audit_logger.log_delete('practice_quizzes', quiz_id, old_record)
        ext._invalidate_practice_cache(old_record.get('scam_type'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/practice-quizzes/reorder', methods=['POST'])
@_auth
@_role('editor', 'admin')
def admin_reorder_practice_quizzes():
    """POST /admin/practice-quizzes/reorder — update display_order for a scam_type."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    data = request.get_json(force=True) or {}
    scam_type = data.get('scam_type', '')
    order = data.get('order', [])

    if not scam_type or not order:
        return jsonify({'error': 'scam_type and order are required'}), 400

    try:
        for idx, qid in enumerate(order):
            supabase_client.table('practice_quizzes').update({'display_order': idx}).eq('id', qid).execute()
        ext._invalidate_practice_cache(scam_type)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_content.route('/admin/practice-quizzes/<int:quiz_id>/copy-to-quiz', methods=['POST'])
@_auth
@_role('editor', 'admin')
def admin_copy_practice_to_quiz(quiz_id):
    """POST /admin/practice-quizzes/<id>/copy-to-quiz — copy practice question to quiz_questions."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    data = request.get_json(force=True) or {}
    difficulty = data.get('difficulty', '')
    if difficulty not in ('easy', 'medium', 'difficult'):
        return jsonify({'error': 'difficulty must be easy, medium, or difficult'}), 400

    try:
        pq_result = supabase_client.table('practice_quizzes').select('*').eq('id', quiz_id).execute()
        if not pq_result.data:
            return jsonify({'error': 'Not found'}), 404
        pq = pq_result.data[0]

        new_record = {
            'question_text': pq.get('question_text', ''),
            'option_1': pq.get('option_1', ''), 'option_2': pq.get('option_2', ''),
            'option_3': pq.get('option_3', ''), 'option_4': pq.get('option_4', ''),
            'correct_answer_index': pq.get('correct_answer_index', 0),
            'explanation': pq.get('explanation', ''),
            'difficulty': difficulty, 'is_active': True,
        }
        result = supabase_client.table('quiz_questions').insert(new_record).execute()
        created = result.data[0] if result.data else new_record
        if ext._audit_logger:
            ext._audit_logger.log_create('quiz_questions', created.get('id'), created)
        ext._invalidate_quiz_cache()
        return jsonify({'id': created.get('id')}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
