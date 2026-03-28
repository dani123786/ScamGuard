"""Public-facing page routes."""
from flask import Blueprint, render_template
from routes.extensions import content_service as _cs_ref
import routes.extensions as ext

public = Blueprint('public', __name__)


@public.route('/')
def index():
    return render_template('index.html')


@public.route('/awareness')
def awareness():
    cs = ext.content_service
    try:
        scams = cs.get_scam_definitions() if cs else {}
    except Exception:
        scams = {}
    return render_template('awareness.html', scams=scams)


@public.route('/awareness/<scam_type>')
def scam_detail(scam_type):
    cs = ext.content_service
    try:
        scam = cs.get_scam_definitions(scam_type=scam_type) if cs else None
        practice_questions = cs.get_practice_quizzes(scam_type=scam_type) if cs else []
    except Exception:
        scam = None
        practice_questions = []
    if not scam:
        return "Scam type not found", 404
    return render_template('scam_detail.html',
                           scam_type=scam_type,
                           scam=scam,
                           practice_questions=practice_questions,
                           video_available=True)


@public.route('/quiz')
def quiz():
    return render_template('quiz.html')


@public.route('/checker')
def checker():
    return render_template('checker.html')


@public.route('/verify')
def verify():
    return render_template('verify.html')


@public.route('/resources')
def resources():
    return render_template('resources.html')


@public.route('/report')
def report():
    return render_template('report.html')
