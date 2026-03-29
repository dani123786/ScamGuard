# ScamGuard — AI-Powered Scam Detection & Education Platform

A web application that helps users identify, report, and learn about online scams using AI-powered analysis backed by a Supabase PostgreSQL database.

---

## Features

- **AI Scam Checker** — Analyze emails, messages, and URLs using Google Gemini AI
- **Scammer Verification** — Check if an email or phone number has been reported as a scammer
- **Scam Reporting** — Submit reports with full AI analysis shown to the user instantly
- **Educational Content** — 10 scam types with videos (Supabase Storage), warning signs, prevention tips, and practice quizzes
- **Knowledge Quiz** — Easy, medium, and difficult levels with instant feedback
- **Live Statistics** — Real-time dashboard of community reports
- **Admin Panel** — Password-protected interface to manage all content and view reports
- **Pakistan Standard Time (PKT)** — All timestamps stored in UTC and displayed in PKT (UTC+5) throughout the system
- **Fully Responsive** — Works on desktop, tablet, and mobile

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · Flask 3.0 (Blueprint architecture) |
| Database | Supabase (PostgreSQL) |
| File Storage | Supabase Storage (educational videos) |
| AI | Google Gemini API (`google-genai 1.68`) |
| Frontend | HTML5 · Bootstrap 5 · Vanilla JS (one file per page) |
| Rate Limiting | Flask-Limiter 3.5 |
| Deployment | Render (WSGI via Gunicorn) |

---

## Project Structure

```
ScamGuard AI INEGRATED/
│
├── app.py                          # App factory: env load, Flask init, shared objects,
│                                   # blueprint registration, entry point
├── requirements.txt                # All Python dependencies (pinned versions)
├── start.bat                       # Windows one-click startup script
├── .env                            # Environment variables — never commit this file
├── .gitignore
└── README.md
│
├── routes/                         # Flask Blueprints — one file per responsibility
│   ├── __init__.py
│   ├── extensions.py               # Shared module-level objects: supabase_client,
│   │                               # content_service, cache_manager, auth helpers,
│   │                               # cache invalidation helpers
│   ├── public.py                   # Public page routes:
│   │                               #   GET /  · /awareness  · /awareness/<scam_type>
│   │                               #   GET /quiz  · /checker  · /verify
│   │                               #   GET /resources  · /report
│   ├── api.py                      # Public JSON API — all /api/* endpoints
│   │                               # Handles PKT timezone conversion (_to_pkt),
│   │                               # AI report analysis, scam checker, stats
│   ├── auth_routes.py              # Admin authentication:
│   │                               #   GET  /admin/login
│   │                               #   POST /admin/auth/login · /admin/auth/logout
│   │                               #   GET  /admin/auth/me · /admin/auth/csrf-token
│   ├── admin_routes.py             # Admin content management (auth-protected):
│   │                               #   GET  /admin/reports  (reports dashboard)
│   │                               #   CRUD /admin/quiz-questions
│   │                               #   CRUD /admin/scam-definitions
│   │                               #   CRUD /admin/practice-quizzes
│   │                               #   POST /admin/practice-quizzes/reorder
│   │                               #   POST /admin/practice-quizzes/<id>/copy-to-quiz
│   │                               #   POST /admin/quiz-questions/bulk
│   └── analytics_routes.py        # Analytics & admin tools (auth-protected):
│                                   #   GET  /admin/analytics
│                                   #   GET  /api/analytics/export
│                                   #   GET  /admin/audit-log
│                                   #   GET  /admin/export/json · /admin/export/csv
│                                   #   POST /admin/import
│                                   #   GET  /admin/content
│                                   #   POST /admin/rollback
│                                   #   GET  /admin/cache/status
│                                   #   POST /admin/cache/clear
│
├── services/                       # Business-logic layer (no Flask dependencies)
│   ├── __init__.py
│   ├── content_service.py          # All database read queries with TTL caching;
│   │                               # get_quiz_questions, get_scam_definitions,
│   │                               # get_practice_quizzes
│   ├── content_validator.py        # Input validation for quiz questions, scam
│   │                               # definitions, and practice quizzes
│   ├── audit_logger.py             # Logs create/update/delete to content_versions
│   │                               # table with before/after snapshots
│   ├── auth.py                     # Admin session auth, RBAC role checks,
│   │                               # CSRF token generation & validation,
│   │                               # password hashing (Werkzeug)
│   ├── cache_manager.py            # Lightweight in-memory TTL cache
│   │                               # (SimpleCacheManager)
│   └── rate_limiter.py             # Flask-Limiter initialisation
│
├── data/                           # AI analysis layer
│   ├── __init__.py
│   └── checkers.py                 # Google Gemini API integration:
│                                   #   analyze_with_ai()         — email / message
│                                   #   analyze_url_with_ai()     — URL phishing check
│                                   #   analyze_report_with_ai()  — submitted report
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Base layout: sidebar nav, Bootstrap, font imports
│   ├── index.html                  # Home page with live community stats
│   ├── awareness.html              # All 10 scam types overview grid
│   ├── scam_detail.html            # Individual scam page: video + practice quiz
│   ├── quiz.html                   # Main knowledge quiz (easy / medium / difficult)
│   ├── checker.html                # AI scam checker (email / message / URL tabs)
│   ├── report.html                 # Report a scam form + AI analysis result panel
│   ├── verify.html                 # Verify a scammer contact
│   ├── resources.html              # Official resources and external links
│   ├── admin.html                  # Admin reports dashboard with search & filters
│   └── admin_login.html            # Admin login page
│
├── static/
│   ├── css/
│   │   └── style.css               # Full responsive application stylesheet
│   └── js/                         # One JavaScript file per page
│       ├── sidebar.js              # Sidebar toggle — loaded on every page via base.html
│       ├── stats.js                # Animated live stats counter — index.html
│       ├── quiz.js                 # Quiz engine: question flow, scoring — quiz.html
│       ├── checker.js              # AI checker: tab switching, result cards — checker.html
│       ├── practice_quiz.js        # Practice quiz engine — scam_detail.html
│       ├── report.js               # Report form + AI analysis result display — report.html
│       ├── verify.js               # Contact verification results — verify.html
│       └── admin_login.js          # Admin login form handler — admin_login.html
│
└── reports/                        # Local flat-file backup of submitted scam reports
    └── .gitkeep                    # Keeps the empty folder tracked in git
```

---

## Database (Supabase)

| Table | Description |
|---|---|
| `reports` | User-submitted scam reports. Stores `scam_type`, `description`, `scammer_contact`, `ai_analysis` (JSONB), `submitted_at` (UTC ISO timestamp) |
| `quiz_questions` | 60 knowledge quiz questions across easy / medium / difficult |
| `scam_definitions` | 10 scam types with descriptions, warning signs, prevention tips, and view counts |
| `practice_quizzes` | 10 practice questions per scam type (100 total), ordered by `display_order` |
| `content_versions` | Full audit trail — every create / update / delete is logged with before/after snapshots |
| `admin_users` | Admin accounts with hashed passwords and role assignments |

Videos are hosted in Supabase Storage (`Videos` bucket) and served via CDN URL.

---

## Setup & Running

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd "ScamGuard AI INEGRATED"
pip install -r requirements.txt
```

### 2. Configure `.env`

Copy the template below and fill in your own values:

```env
# Flask
SECRET_KEY=your-long-random-secret-key
FLASK_ENV=development
PORT=5000

# Supabase — Project Settings > API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Content source: auto | database-only | file-only
DATABASE_MODE=auto
```

> ⚠️ Never commit `.env` to version control. It is already listed in `.gitignore`.

### 3. Run

```bash
# Windows (double-click or run):
start.bat

# Or directly:
python app.py
```

Open `http://localhost:5000`

---

## Admin Access

Navigate to `http://localhost:5000/admin/login`

All `/admin/*` routes are session-protected. Unauthenticated requests are automatically redirected to the login page. Role-based access control (RBAC) restricts write operations (`editor` and `admin` roles only).

---

## API Reference

### Public Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/stats` | Live community statistics (total reports, high-risk count, top scam type) |
| `GET` | `/api/scams` | All active scam definitions |
| `GET` | `/api/scams/<scam_type>` | Single scam definition (also increments view count) |
| `GET` | `/api/quiz/questions?difficulty=easy` | Quiz questions for a given difficulty |
| `POST` | `/api/quiz/submit` | Submit quiz answers, returns score + explanations |
| `GET` | `/api/practice/<scam_type>` | Practice questions for a scam type |
| `POST` | `/api/practice/submit` | Submit practice answers, tracks completion stats |
| `POST` | `/api/check` | AI analysis of email / message / url content |
| `POST` | `/api/check/url` | Dedicated URL phishing analysis |
| `POST` | `/api/report` | Submit a scam report; returns AI analysis to the user |
| `POST` | `/api/verify` | Check if a contact has been previously reported |

### Admin Endpoints (auth required)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/reports` | Reports dashboard (HTML) |
| `GET/POST` | `/admin/quiz-questions` | List / create quiz questions |
| `PUT/DELETE` | `/admin/quiz-questions/<id>` | Update / soft-delete a question |
| `POST` | `/admin/quiz-questions/bulk` | Bulk delete or change difficulty |
| `GET/POST` | `/admin/scam-definitions` | List / create scam definitions |
| `PUT/DELETE` | `/admin/scam-definitions/<id>` | Update / soft-delete a definition |
| `GET/POST` | `/admin/practice-quizzes` | List / create practice quizzes |
| `PUT/DELETE` | `/admin/practice-quizzes/<id>` | Update / soft-delete a quiz |
| `POST` | `/admin/practice-quizzes/reorder` | Update display order |
| `POST` | `/admin/practice-quizzes/<id>/copy-to-quiz` | Copy to quiz_questions table |
| `GET` | `/admin/analytics` | Analytics dashboard (HTML) |
| `GET` | `/admin/audit-log` | Audit trail of all content changes |
| `GET` | `/admin/export/json` | Export all content as JSON |
| `GET` | `/admin/export/csv` | Export reports as CSV |
| `POST` | `/admin/import` | Import content from JSON |
| `POST` | `/admin/rollback` | Roll back a content change |
| `GET/POST` | `/admin/cache/status` · `/admin/cache/clear` | Cache management |

---

## Timezone Handling (PKT)

All timestamps in this system follow a consistent two-step approach:

1. **Storage** — `submitted_at` is saved as a UTC ISO 8601 string (e.g. `2026-03-28T08:30:00+00:00`) so Supabase can sort and filter correctly.
2. **Display** — The `_to_pkt()` helper in `routes/api.py` converts any UTC timestamp to **Pakistan Standard Time (UTC+5)** before it is rendered in the admin portal or returned in API responses.

This means all times shown in the admin dashboard, verify results, and report confirmations are in PKT.

---

## Deployment (Render)

1. Push to GitHub
2. Import the repo at [render.com](https://render.com)
3. Add the following environment variables in the Rendet dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SECRET_KEY`
   - `GEMINI_API_KEY`
--