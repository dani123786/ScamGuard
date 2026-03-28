"""Analytics, audit log, import/export, cache, rollback, and dashboard routes."""
import csv
import io
from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, request, jsonify, make_response, session
import routes.extensions as ext

analytics = Blueprint('analytics', __name__)


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


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def _build_analytics_response():
    """Build analytics JSON (shared by admin and export endpoints)."""
    supabase_client = ext.supabase_client
    empty = {
        'question_metrics': [],
        'most_viewed_scams': [],
        'practice_completion': [],
        'low_correct_rate_questions': [],
    }

    if supabase_client is None:
        return jsonify(empty)

    try:
        qq_result = supabase_client.table('quiz_questions').select(
            'id, question_text, difficulty, correct_count, incorrect_count'
        ).eq('is_active', True).execute()
        question_metrics = []
        for q in (qq_result.data or []):
            correct = q.get('correct_count', 0) or 0
            incorrect = q.get('incorrect_count', 0) or 0
            total = correct + incorrect
            rate = (correct / total) if total > 0 else None
            question_metrics.append({
                'id': q.get('id'),
                'question_text': q.get('question_text', ''),
                'difficulty': q.get('difficulty', ''),
                'correct_count': correct,
                'incorrect_count': incorrect,
                'correct_rate': rate,
            })
        question_metrics.sort(key=lambda x: (x['correct_rate'] is None, x['correct_rate'] or 0))

        sd_result = supabase_client.table('scam_definitions').select(
            'scam_type, title, view_count'
        ).eq('is_active', True).execute()
        most_viewed = sorted(
            [{'scam_type': s.get('scam_type'), 'title': s.get('title'),
              'view_count': s.get('view_count', 0) or 0}
             for s in (sd_result.data or [])],
            key=lambda x: x['view_count'],
            reverse=True,
        )

        pq_result = supabase_client.table('practice_quizzes').select(
            'scam_type, completion_count'
        ).eq('is_active', True).execute()
        pq_by_scam = {}
        for q in (pq_result.data or []):
            st = q.get('scam_type', '')
            if st not in pq_by_scam:
                pq_by_scam[st] = {'total': 0, 'completion_sum': 0}
            pq_by_scam[st]['total'] += 1
            pq_by_scam[st]['completion_sum'] += q.get('completion_count', 0) or 0
        practice_completion = [
            {
                'scam_type': st,
                'total_questions': v['total'],
                'avg_completion_count': (v['completion_sum'] / v['total']) if v['total'] > 0 else 0,
            }
            for st, v in pq_by_scam.items()
        ]

        low_rate = [q for q in question_metrics if q['correct_rate'] is not None and q['correct_rate'] < 0.5]
        if not low_rate:
            low_rate = question_metrics

        return jsonify({
            'question_metrics': question_metrics,
            'most_viewed_scams': most_viewed,
            'practice_completion': practice_completion,
            'low_correct_rate_questions': low_rate,
        })
    except Exception as e:
        print(f"[!] Analytics error: {e}")
        return jsonify(empty)


@analytics.route('/admin/analytics', methods=['GET'])
@_auth
def admin_analytics():
    """GET /admin/analytics — analytics dashboard data."""
    return _build_analytics_response()


@analytics.route('/api/analytics/export', methods=['GET'])
def analytics_export():
    """GET /api/analytics/export — public analytics data export."""
    return _build_analytics_response()


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

@analytics.route('/admin/audit-log', methods=['GET'])
@_auth
def admin_audit_log():
    """GET /admin/audit-log — paginated audit log with filters."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'logs': [], 'total': 0, 'page': 1, 'pages': 0})

    table_filter = request.args.get('table', '').strip()
    change_type = request.args.get('change_type', '').strip()
    changed_by = request.args.get('changed_by', '').strip()
    from_date = request.args.get('from_date', '').strip()
    to_date = request.args.get('to_date', '').strip()
    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    per_page = 20

    try:
        query = supabase_client.table('content_versions').select('*', count='exact')
        if table_filter:
            query = query.eq('table_name', table_filter)
        if change_type:
            query = query.eq('change_type', change_type)
        if changed_by:
            query = query.eq('changed_by', changed_by)
        if from_date:
            query = query.gte('changed_at', from_date)
        if to_date:
            query = query.lte('changed_at', to_date)
        query = query.order('changed_at', desc=True)
        result = query.execute()
        logs = result.data or []
        total = result.count if result.count is not None else len(logs)
        pages = max(1, (total + per_page - 1) // per_page)
        start = (page - 1) * per_page
        return jsonify({'logs': logs[start:start + per_page],
                        'total': total, 'page': page, 'pages': pages})
    except Exception as e:
        print(f"[!] Audit log error: {e}")
        return jsonify({'logs': [], 'total': 0, 'page': 1, 'pages': 0})


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

@analytics.route('/admin/export/json', methods=['GET'])
@_auth
def admin_export_json():
    """GET /admin/export/json — export all active content as JSON."""
    supabase_client = ext.supabase_client
    exported_at = datetime.now(timezone.utc).isoformat()

    if supabase_client is None:
        return jsonify({
            'exported_at': exported_at,
            'version': '1.0',
            'quiz_questions': [],
            'scam_definitions': [],
            'practice_quizzes': [],
        })

    try:
        qq = supabase_client.table('quiz_questions').select('*').eq('is_active', True).execute().data or []
        sd = supabase_client.table('scam_definitions').select('*').eq('is_active', True).execute().data or []
        pq = supabase_client.table('practice_quizzes').select('*').eq('is_active', True).execute().data or []
        return jsonify({
            'exported_at': exported_at,
            'version': '1.0',
            'quiz_questions': qq,
            'scam_definitions': sd,
            'practice_quizzes': pq,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics.route('/admin/export/csv', methods=['GET'])
@_auth
def admin_export_csv():
    """GET /admin/export/csv — export quiz_questions as CSV."""
    supabase_client = ext.supabase_client
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'question_text', 'difficulty', 'correct_answer_index', 'explanation'])

    if supabase_client is not None:
        try:
            result = supabase_client.table('quiz_questions').select(
                'id, question_text, difficulty, correct_answer_index, explanation'
            ).eq('is_active', True).execute()
            for q in (result.data or []):
                writer.writerow([
                    q.get('id', ''), q.get('question_text', ''),
                    q.get('difficulty', ''), q.get('correct_answer_index', ''),
                    q.get('explanation', ''),
                ])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    csv_data = output.getvalue()
    resp = make_response(csv_data)
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=quiz_questions.csv'
    return resp


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

@analytics.route('/admin/import', methods=['POST'])
@_auth
@_role('editor', 'admin')
def admin_import_content():
    """POST /admin/import — import content from JSON body."""
    supabase_client = ext.supabase_client
    mode = request.args.get('mode', 'preview')
    data = request.get_json(force=True) or {}

    quiz_questions_in = data.get('quiz_questions', [])
    scam_definitions_in = data.get('scam_definitions', [])
    practice_quizzes_in = data.get('practice_quizzes', [])

    if isinstance(quiz_questions_in, dict):
        flat = []
        for diff, qs in quiz_questions_in.items():
            for q in qs:
                flat.append({**q, 'difficulty': diff})
        quiz_questions_in = flat
    if isinstance(scam_definitions_in, dict):
        flat = []
        for st, s in scam_definitions_in.items():
            flat.append({**s, 'scam_type': st})
        scam_definitions_in = flat
    if isinstance(practice_quizzes_in, dict):
        flat = []
        for st, qs in practice_quizzes_in.items():
            for q in qs:
                flat.append({**q, 'scam_type': st})
        practice_quizzes_in = flat

    errors = []
    valid_qq, valid_sd, valid_pq = [], [], []
    validator = ext._content_validator

    for i, q in enumerate(quiz_questions_in):
        if validator:
            ok, errs = validator.validate_quiz_question(q)
            if not ok:
                errors.append(f'quiz_questions[{i}]: {"; ".join(errs)}')
                continue
        valid_qq.append(q)

    for i, s in enumerate(scam_definitions_in):
        if validator:
            ok, errs = validator.validate_scam_definition(s)
            if not ok:
                errors.append(f'scam_definitions[{i}]: {"; ".join(errs)}')
                continue
        valid_sd.append(s)

    for i, q in enumerate(practice_quizzes_in):
        if validator:
            ok, errs = validator.validate_practice_quiz(q)
            if not ok:
                errors.append(f'practice_quizzes[{i}]: {"; ".join(errs)}')
                continue
        valid_pq.append(q)

    if mode == 'preview':
        return jsonify({'preview': {
            'quiz_questions': len(valid_qq),
            'scam_definitions': len(valid_sd),
            'practice_quizzes': len(valid_pq),
            'errors': errors,
        }})

    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    imported = {'quiz_questions': 0, 'scam_definitions': 0, 'practice_quizzes': 0}
    skipped = 0

    for q in valid_qq:
        options = q.get('options', [])
        record = {
            'question_text': q.get('question_text') or q.get('question', ''),
            'option_1': options[0] if len(options) > 0 else q.get('option_1', ''),
            'option_2': options[1] if len(options) > 1 else q.get('option_2', ''),
            'option_3': options[2] if len(options) > 2 else q.get('option_3', ''),
            'option_4': options[3] if len(options) > 3 else q.get('option_4', ''),
            'correct_answer_index': q.get('correct_answer_index') if q.get('correct_answer_index') is not None else q.get('correct', 0),
            'explanation': q.get('explanation', ''),
            'difficulty': q.get('difficulty', 'easy'),
            'is_active': True,
        }
        try:
            existing = supabase_client.table('quiz_questions').select('id').eq('question_text', record['question_text']).eq('difficulty', record['difficulty']).execute()
            if existing.data:
                skipped += 1
                continue
            result = supabase_client.table('quiz_questions').insert(record).execute()
            if result.data and ext._audit_logger:
                ext._audit_logger.log_create('quiz_questions', result.data[0].get('id'), result.data[0])
            imported['quiz_questions'] += 1
        except Exception as e:
            errors.append(f'quiz_questions insert error: {e}')

    for s in valid_sd:
        record = {
            'scam_type': s.get('scam_type', ''),
            'title': s.get('title', ''), 'icon': s.get('icon', ''),
            'color': s.get('color', ''), 'description': s.get('description', ''),
            'warning_signs': s.get('warning_signs', []),
            'prevention_tips': s.get('prevention_tips') or s.get('prevention', []),
            'is_active': True,
        }
        try:
            existing = supabase_client.table('scam_definitions').select('id').eq('scam_type', record['scam_type']).execute()
            if existing.data:
                skipped += 1
                continue
            result = supabase_client.table('scam_definitions').insert(record).execute()
            if result.data and ext._audit_logger:
                ext._audit_logger.log_create('scam_definitions', result.data[0].get('id'), result.data[0])
            imported['scam_definitions'] += 1
        except Exception as e:
            errors.append(f'scam_definitions insert error: {e}')

    for q in valid_pq:
        options = q.get('options', [])
        record = {
            'scam_type': q.get('scam_type', ''),
            'question_text': q.get('question_text') or q.get('question', ''),
            'option_1': options[0] if len(options) > 0 else q.get('option_1', ''),
            'option_2': options[1] if len(options) > 1 else q.get('option_2', ''),
            'option_3': options[2] if len(options) > 2 else q.get('option_3', ''),
            'option_4': options[3] if len(options) > 3 else q.get('option_4', ''),
            'correct_answer_index': q.get('correct_answer_index') if q.get('correct_answer_index') is not None else q.get('correct', 0),
            'explanation': q.get('explanation', ''),
            'is_active': True,
        }
        try:
            existing = supabase_client.table('practice_quizzes').select('id').eq('scam_type', record['scam_type']).eq('question_text', record['question_text']).execute()
            if existing.data:
                skipped += 1
                continue
            result = supabase_client.table('practice_quizzes').insert(record).execute()
            if result.data and ext._audit_logger:
                ext._audit_logger.log_create('practice_quizzes', result.data[0].get('id'), result.data[0])
            imported['practice_quizzes'] += 1
        except Exception as e:
            errors.append(f'practice_quizzes insert error: {e}')

    ext._invalidate_quiz_cache()
    ext._invalidate_scam_cache()

    return jsonify({'imported': imported, 'skipped': skipped, 'errors': errors})


# ---------------------------------------------------------------------------
# Content dashboard
# ---------------------------------------------------------------------------

@analytics.route('/admin/content', methods=['GET'])
@_auth
def admin_content_dashboard():
    """GET /admin/content — content statistics dashboard."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({
            'quiz_questions': {'total': 0, 'active': 0},
            'scam_definitions': {'total': 0, 'active': 0},
            'practice_quizzes': {'total': 0, 'active': 0},
            'recent_changes': [],
        })

    try:
        qq_result = supabase_client.table('quiz_questions').select('id, is_active', count='exact').execute()
        qq_all = qq_result.data or []
        qq_total = qq_result.count if qq_result.count is not None else len(qq_all)
        qq_active = sum(1 for q in qq_all if q.get('is_active', True))

        sd_result = supabase_client.table('scam_definitions').select('id, is_active', count='exact').execute()
        sd_all = sd_result.data or []
        sd_total = sd_result.count if sd_result.count is not None else len(sd_all)
        sd_active = sum(1 for s in sd_all if s.get('is_active', True))

        pq_result = supabase_client.table('practice_quizzes').select('id, is_active', count='exact').execute()
        pq_all = pq_result.data or []
        pq_total = pq_result.count if pq_result.count is not None else len(pq_all)
        pq_active = sum(1 for q in pq_all if q.get('is_active', True))

        recent_result = supabase_client.table('content_versions').select('*').order('changed_at', desc=True).limit(5).execute()
        recent_changes = recent_result.data or []

        return jsonify({
            'quiz_questions': {'total': qq_total, 'active': qq_active},
            'scam_definitions': {'total': sd_total, 'active': sd_active},
            'practice_quizzes': {'total': pq_total, 'active': pq_active},
            'recent_changes': recent_changes,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------

@analytics.route('/admin/rollback', methods=['POST'])
@_auth
@_role('admin')
def admin_rollback():
    """POST /admin/rollback — restore a previous content version."""
    supabase_client = ext.supabase_client
    if supabase_client is None:
        return jsonify({'error': 'Database not available'}), 503

    data = request.get_json(force=True) or {}
    version_id = data.get('version_id')
    content_type = data.get('content_type')
    record_id = data.get('record_id')

    try:
        if version_id is not None:
            ver_result = supabase_client.table('content_versions').select('*').eq('id', version_id).execute()
            if not ver_result.data:
                return jsonify({'error': 'Version not found'}), 404
            version = ver_result.data[0]
            table = version.get('table_name')
            rec_id = version.get('record_id')
            old_value = version.get('old_value') or {}
        elif content_type and record_id is not None:
            table = content_type
            rec_id = record_id
            ver_result = supabase_client.table('content_versions').select('*').eq('table_name', table).eq('record_id', rec_id).order('changed_at', desc=True).limit(1).execute()
            if not ver_result.data:
                return jsonify({'error': 'No version history found for this record'}), 404
            version = ver_result.data[0]
            old_value = version.get('old_value') or {}
        else:
            return jsonify({'error': 'Provide version_id OR content_type + record_id'}), 400

        if not old_value:
            return jsonify({'error': 'No old_value to restore'}), 400

        current_result = supabase_client.table(table).select('*').eq('id', rec_id).execute()
        current_value = current_result.data[0] if current_result.data else {}

        restore_data = {k: v for k, v in old_value.items() if k not in ('id', 'created_at', 'updated_at')}
        supabase_client.table(table).update(restore_data).eq('id', rec_id).execute()

        if ext._audit_logger:
            actor = session.get('username', 'admin')
            ext._audit_logger.log_rollback(table, rec_id, current_value, old_value,
                                           changed_by=actor, reason='admin rollback')

        if table == 'quiz_questions':
            ext._invalidate_quiz_cache()
        elif table == 'scam_definitions':
            ext._invalidate_scam_cache(old_value.get('scam_type'))
        elif table == 'practice_quizzes':
            ext._invalidate_practice_cache(old_value.get('scam_type'))

        return jsonify({'success': True, 'rolled_back': {'table': table, 'record_id': rec_id}})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

@analytics.route('/admin/cache/status', methods=['GET'])
@_auth
def admin_cache_status():
    """GET /admin/cache/status — return cache statistics."""
    return jsonify({
        'cache_keys': len(ext._cache_manager._store),
        'backend': 'in-memory',
    })


@analytics.route('/admin/cache/clear', methods=['POST'])
@_auth
@_role('admin')
def admin_cache_clear():
    """POST /admin/cache/clear — clear all cached entries."""
    ext._cache_manager.clear()
    return jsonify({'cleared': True})
