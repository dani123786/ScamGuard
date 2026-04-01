# ScamGuard — Online Scam Awareness & Protection System

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-2.3+-lightgrey)
![AI](https://img.shields.io/badge/AI-Gemini%20Powered-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## 🔗 Live Demo

**[https://scamguard-9x63.onrender.com](https://scamguard-9x63.onrender.com)**

---

## Overview

ScamGuard is a full-stack, AI-powered web platform designed to educate users about online scams and give them practical tools to identify, verify, and report digital threats. Powered by **Google Gemini AI**, it goes beyond static education — offering real-time scam analysis, a community-driven contact verification database, an interactive quiz system, and an admin dashboard for managing reports.

---

## Problem Statement

Online scams are a growing global threat, costing individuals and businesses billions of dollars annually. According to the FBI's Internet Crime Report, losses from cybercrime exceeded **$10 billion in 2023** alone. The problem is getting worse:

- **Rising sophistication** — scammers use AI, deepfakes, and social engineering to deceive victims
- **Lack of awareness** — many people don't recognise warning signs until it's too late
- **Limited education** — traditional awareness methods are passive and forgettable
- **Accessibility gap** — scam education resources are often scattered and hard to navigate

Victims often feel embarrassed to report scams, allowing criminals to continue targeting others. ScamGuard addresses this with an accessible, interactive, AI-powered platform that educates people *before* they become victims.

---

## Features

### 🤖 AI Scam Checker (Gemini AI)
Paste any email, message, or URL and receive an instant, context-aware analysis powered by Google Gemini AI. Unlike keyword-based tools, the AI understands intent, tone, and structure — detecting phishing, brand impersonation, investment fraud, social engineering, and more.

### 🔍 Verify Contact
Search a community-reported database of known scammer emails and phone numbers. If a contact has been reported before, users see detailed history and risk statistics — helping them make informed decisions before engaging.

### 📚 Scam Awareness (10 Scam Types)
Comprehensive educational modules covering:
- Phishing Scams
- Cryptocurrency Scams
- Investment & Ponzi Schemes
- Tech Support Scams
- E-Commerce & Online Shopping Scams
- Identity Theft & Data Breach
- Lottery & Prize Scams
- Employment & Job Scams
- Social Media & Impersonation
- Deepfake Scams

Each module includes real-world examples, red-flag warning signs, prevention tips, and an educational video.

### 🧠 Interactive Quiz System
- **3 difficulty levels** — Easy, Medium, Difficult
- **60 total questions** — 20 per difficulty
- **100 practice questions** — 10 per scam type
- Personalised results with instant feedback and explanations

### 📝 Scam Reporting (3-Step Form)
A guided multi-step reporting form that captures scam type, contact method, incident date, description, scammer contact info, financial loss, and optional reporter email. Reports are saved to the community database and help others stay protected.

### 📊 Live Dashboard Stats
The homepage displays real-time statistics from the database:
- Total community reports
- High-risk detections
- Total money lost reported
- Reports this month
- Most common scam type and contact method

### 🛡️ Admin Dashboard
A protected admin panel for managing submitted reports, viewing community data, and monitoring platform activity.

### 📖 Resources
Verified links and official contacts for reporting scams to authorities such as the FTC, IC3, and others.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.8+, Flask 2.3+ |
| AI | Google Gemini API |
| Frontend | HTML5, CSS3, Bootstrap 5, Font Awesome |
| Database | SQLite / configured DB |
| Deployment | Render |
| Version Control | Git, GitHub |

---

## Project Structure

```
scamguard/
├── app.py                      # Main Flask application & routes
├── config.py                   # Configuration and environment variables
├── requirements.txt            # Python dependencies
├── vercel.json                 # (legacy) Vercel deployment config
├── .gitignore
├── README.md
├── data/                       # Application data modules
│   ├── __init__.py
│   ├── scams.py                # Scam awareness content & descriptions
│   ├── practice_quizzes.py     # 100 practice quiz questions (10 per scam type)
│   ├── quiz_questions.py       # 60 main quiz questions (easy/medium/difficult)
│   └── checkers.py             # Scam check logic (legacy rule-based)
├── static/
│   ├── css/
│   │   └── style.css           # Responsive styles
│   └── videos/                 # 10 educational scam awareness videos
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with sidebar navigation
│   ├── index.html              # Homepage with live stats
│   ├── awareness.html          # Scam type overview grid
│   ├── scam_detail.html        # Individual scam detail + practice quiz
│   ├── quiz.html               # Main quiz (3 difficulty levels)
│   ├── checker.html            # AI Scam Checker (Gemini)
│   ├── verify.html             # Verify Contact tool
│   ├── report.html             # 3-step scam reporting form
│   ├── resources.html          # External resources & authorities
│   └── admin/                  # Admin dashboard templates
├── reports/                    # Locally saved report backups
├── tests/
│   └── test_app.py             # Unit tests
└── docs/                       # Documentation
```

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Google Gemini API key

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/dani123786/ScamGuard.git
cd ScamGuard
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set environment variables**

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

**5. Run the application**
```bash
python app.py
```

**6. Open in browser**
```
http://127.0.0.1:5000
```

---

## Deployment

### Deploy to Render (Recommended)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and create a new **Web Service**
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`
6. Add environment variables (`GEMINI_API_KEY`, `SECRET_KEY`) in the Render dashboard
7. Deploy

### Deploy to Heroku

```bash
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
git push heroku main
```

### Deploy to PythonAnywhere

1. Upload files to PythonAnywhere
2. Set up a virtual environment and install requirements
3. Configure the WSGI file to point to `app.py`
4. Add environment variables in the dashboard
5. Reload the web app

---

## Responsive Design

ScamGuard is fully responsive and works on all devices:

- **Smartphones** (iOS & Android) — touch-optimised, slide-in sidebar, full-width buttons
- **Tablets** — adaptive layout with readable font sizes
- **Laptops & Desktops** — always-visible sidebar, keyboard shortcut `Ctrl+B` to toggle, multi-column layouts, hover effects

---

## Content Statistics

| Category | Count |
|---|---|
| Scam types covered | 10 |
| Educational videos | 10 |
| Practice quiz questions | 100 |
| Main quiz questions | 60 |
| Quiz difficulty levels | 3 |
| Detection tools | 3 (AI Checker, Verify Contact, Report) |

---

## Testing

```bash
python -m pytest tests/
```

To test responsiveness, open browser DevTools (`F12`), toggle device mode (`Ctrl+Shift+M`), and test at different screen sizes.

---

## Roadmap

- [ ] User authentication and personalised progress tracking
- [ ] Real-time AI-powered scam news feed
- [ ] Mobile app (iOS & Android)
- [ ] Multi-language support
- [ ] Enhanced admin analytics dashboard
- [ ] Public API for third-party integrations
- [ ] Browser extension for real-time URL checking

---

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgements

- [Google Gemini AI](https://ai.google.dev/) — for powering the scam checker
- [Bootstrap 5](https://getbootstrap.com/) — for the responsive UI framework
- [Font Awesome](https://fontawesome.com/) — for icons
- [Flask](https://flask.palletsprojects.com/) — for the web framework
- [Render](https://render.com/) — for hosting

---

## Support

For support, please open an issue in the [GitHub repository](https://github.com/dani123786/ScamGuard/issues).

---

**Made with care for online safety and scam awareness.**

**Version:** 2.0.0 | **Status:** Production Ready | **Last Updated:** April 2026
