from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from data.scams import SCAMS_DATA
from data.practice_quizzes import PRACTICE_QUIZZES
from data.quiz_questions import QUIZ_QUESTIONS
from data.checkers import check_email, check_message, evaluate_risk

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/awareness')
def awareness():
    return render_template('awareness.html', scams=SCAMS_DATA)

@app.route('/awareness/<scam_type>')
def scam_detail(scam_type):
    if scam_type in SCAMS_DATA:
        # Get practice quiz questions for this scam type
        practice_questions = PRACTICE_QUIZZES.get(scam_type, [])
        
        # Check if video exists for this scam type
        video_path = os.path.join('static', 'videos', f'{scam_type}.mp4')
        video_available = os.path.exists(video_path)
        
        return render_template('scam_detail.html', 
                             scam_type=scam_type, 
                             scam=SCAMS_DATA[scam_type],
                             practice_questions=practice_questions,
                             video_available=video_available)
    return "Scam type not found", 404

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/api/quiz/questions')
def get_quiz_questions():
    difficulty = request.args.get('difficulty', 'easy')
    if difficulty in QUIZ_QUESTIONS:
        return jsonify(QUIZ_QUESTIONS[difficulty])
    return jsonify(QUIZ_QUESTIONS['easy'])

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.json
    answers = data.get('answers', [])
    difficulty = data.get('difficulty', 'easy')
    user_name = data.get('name', 'Anonymous')
    
    questions = QUIZ_QUESTIONS.get(difficulty, QUIZ_QUESTIONS['easy'])
    score = sum(1 for i, ans in enumerate(answers) if ans == questions[i]['correct'])
    total = len(questions)
    percentage = (score / total) * 100
    
    return jsonify({
        'score': score,
        'total': total,
        'percentage': percentage,
        'name': user_name,
        'difficulty': difficulty,
        'results': [
            {
                'correct': answers[i] == questions[i]['correct'],
                'explanation': questions[i]['explanation']
            }
            for i in range(len(answers))
        ]
    })

@app.route('/checker')
def checker():
    return render_template('checker.html')

@app.route('/api/check', methods=['POST'])
def check_scam():
    data = request.json
    check_type = data.get('type')
    content = data.get('content', '')

    if check_type == 'email':
        risk_score, warnings = check_email(content)
    elif check_type == 'message':
        risk_score, warnings = check_message(content)
    else:
        return jsonify({'error': 'Invalid check type'}), 400

    return jsonify(evaluate_risk(risk_score, warnings))

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/api/report', methods=['POST'])
def submit_report():
    data = request.json
    
    report_body = f"""
    NEW SCAM REPORT SUBMISSION
    ========================
    
    Report Details:
    ---------------
    Scam Type: {data.get('scam_type', 'Not specified')}
    Contact Method: {data.get('contact_method', 'Not specified')}
    Date of Incident: {data.get('incident_date', 'Not specified')}
    
    Description:
    {data.get('description', 'No description provided')}
    
    Scammer Information:
    {data.get('scammer_contact', 'No contact information provided')}
    
    Financial Loss:
    Lost Money: {data.get('lost_money', 'No')}
    Amount: {data.get('amount', 'N/A')}
    
    Reporter Contact:
    {data.get('reporter_email', 'Anonymous')}
    
    Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ========================
    This report was submitted through ScamGuard Online Scam Awareness System.
    """
    
    save_report_to_file(data, report_body)
    
    return jsonify({
        'success': True,
        'message': 'Your report has been recorded and will help others recognize and avoid this type of scam.'
    })

def save_report_to_file(data, email_body):
    """Save report to a local file as backup"""
    try:
        # Create reports directory if it doesn't exist
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/scam_report_{timestamp}.txt"
        
        # Write report to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(email_body)
            f.write("\n\n--- RAW DATA ---\n")
            f.write(str(data))
        
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False

if __name__ == '__main__':
    app.run(debug=True)