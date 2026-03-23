# 📁 Project Organization

## 📂 Current Project Structure

```
scamguard/
├── app.py                  # Main Flask application (routes only)
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment config
├── .gitignore
├── README.md
│
├── data/                   # Application data & logic
│   ├── __init__.py
│   ├── scams.py            # Scam awareness data (10 scam types)
│   ├── practice_quizzes.py # Practice quiz questions (10 per scam type)
│   ├── quiz_questions.py   # Main quiz questions (easy/medium/difficult)
│   └── checkers.py         # Email & message scam check logic
│
├── static/
│   ├── css/
│   │   └── style.css       # Responsive styles
│   └── videos/             # Educational videos (10 files)
│
├── templates/              # HTML templates
│   ├── base.html           # Shared layout & sidebar
│   ├── index.html
│   ├── awareness.html
│   ├── scam_detail.html
│   ├── quiz.html
│   ├── checker.html
│   ├── report.html
│   └── resources.html
│
├── reports/                # Saved scam reports (local only)
│   └── .gitkeep
│
├── tests/
│   └── test_app.py
│
└── docs/                   # Documentation
    ├── START_HERE.md
    ├── QUICKSTART.md
    ├── DEPLOYMENT.md
    ├── TROUBLESHOOTING.md
    ├── guides/
    │   ├── PROJECT_ORGANIZATION.md  ← this file
    │   └── RESPONSIVE_REFERENCE.md
    └── deployment/
        ├── DEPLOYMENT_CHECKLIST.md
        └── CLEANUP_INSTRUCTIONS.md
```

## 🗂️ Data Layer (`data/`)

All large data dictionaries and business logic live here, keeping `app.py` focused on routing only.

| File | Contents |
|------|----------|
| `scams.py` | `SCAMS_DATA` — info, warning signs, tips for 10 scam types |
| `practice_quizzes.py` | `PRACTICE_QUIZZES` — 10 questions per scam type (100 total) |
| `quiz_questions.py` | `QUIZ_QUESTIONS` — 20 questions each for easy/medium/difficult |
| `checkers.py` | `check_email()`, `check_message()`, `evaluate_risk()` functions |

## 🌐 Routes in `app.py`

| Route | Purpose |
|-------|---------|
| `/` | Home page |
| `/awareness` | Scam types list |
| `/awareness/<scam_type>` | Individual scam detail |
| `/quiz` | Quiz page |
| `/api/quiz/questions` | Fetch questions by difficulty |
| `/api/quiz/submit` | Score a quiz submission |
| `/checker` | Scam checker page |
| `/api/check` | Analyze email or message content |
| `/resources` | Resources page |
| `/report` | Report a scam page |
| `/api/report` | Save a scam report to file |
