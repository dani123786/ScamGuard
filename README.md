# 🛡️ ScamGuard - Online Scam Awareness System

A comprehensive web application to educate users about online scams and provide tools to identify potential scams.

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Flask](https://img.shields.io/badge/flask-2.3+-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

### Scam Awareness
- **10 Scam Types Covered**: Phishing, Cryptocurrency, Investment, Tech Support, Online Shopping, Identity Theft, Lottery, Employment, Social Media, and Deepfake scams
- **Educational Videos**: Professional videos for each scam type (10/10 complete)
- **Interactive Practice Quizzes**: 10 questions per scam type (100 total)
- **Warning Signs & Prevention Tips**: Detailed information for each scam

### Interactive Quiz System
- **3 Difficulty Levels**: Easy, Medium, and Difficult
- **60 Total Questions**: 20 questions per difficulty level
- **Instant Feedback**: Explanations for each answer
- **Score Tracking**: Track your progress and knowledge

### Scam Checker Tool
- **Email Analysis**: Detect phishing indicators in emails
- **Message Scanning**: Analyze messages for scam characteristics
- **Risk Scoring**: Get a risk assessment with recommendations

### Scam Reporting System
- **Report Incidents**: Submit scam reports saved locally
- **Anonymous Reporting**: Optional reporter information

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/scamguard.git
cd scamguard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open in browser**
```
http://127.0.0.1:5000
```

## Responsive Design

ScamGuard is fully responsive and works on:
- Smartphones (iOS & Android)
- Tablets (iPad, Android tablets)
- Laptops (all screen sizes)
- Desktop Computers (HD to 4K)

### Mobile Features
- Touch-optimized interface
- Slide-in sidebar navigation
- Full-width buttons
- Optimized font sizes
- Responsive videos

### Desktop Features
- Always-visible sidebar
- Keyboard shortcuts (Ctrl+B to toggle sidebar)
- Hover effects
- Multi-column layouts

## Project Structure

```
scamguard/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment config
├── .gitignore
├── README.md
├── data/                   # Application data
│   ├── __init__.py
│   ├── scams.py            # Scam awareness data
│   ├── practice_quizzes.py # Practice quiz questions
│   ├── quiz_questions.py   # Main quiz questions (easy/medium/difficult)
│   └── checkers.py         # Email & message scam check logic
├── static/
│   ├── css/
│   │   └── style.css       # Responsive styles
│   └── videos/             # Educational videos (10 files)
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── awareness.html
│   ├── scam_detail.html
│   ├── quiz.html
│   ├── checker.html
│   ├── report.html
│   └── resources.html
├── reports/                # Saved scam reports
├── tests/
│   └── test_app.py
└── docs/                   # Documentation
```

## 🎬 Educational Videos

All 10 scam awareness videos are included:
- Phishing Scams
- Cryptocurrency Scams
- Investment & Ponzi Schemes
- Tech Support Scams
- E-Commerce & Shopping Scams
- Identity Theft & Data Breach
- Lottery & Prize Scams
- Employment & Job Scams
- Social Media & Impersonation
- Deepfake Scams

## Configuration

No special configuration required. Reports are saved locally to the `reports/` folder.

## Deployment

### Deploy to Vercel

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Deploy**
```bash
vercel
```

3. **Follow the prompts** to complete deployment

### Deploy to Heroku

1. **Create Heroku app**
```bash
heroku create your-app-name
```

2. **Deploy**
```bash
git push heroku main
```

### Deploy to PythonAnywhere

1. Upload files to PythonAnywhere
2. Set up virtual environment
3. Configure WSGI file
4. Reload web app

## Testing

### Run Tests
```bash
python -m pytest tests/
```

### Test Responsiveness
1. Open browser DevTools (F12)
2. Toggle device mode (Ctrl+Shift+M)
3. Test different screen sizes

### Test on Mobile
1. Find your computer's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. On phone browser: `http://YOUR_IP:5000`
3. Ensure phone and computer are on same WiFi

## Statistics

- **10 Scam Types**: Comprehensive coverage
- **10 Educational Videos**: Professional content
- **160 Quiz Questions**: 100 practice + 60 main quiz
- **2 Detection Tools**: Scam checker, reporting
- **Fully Responsive**: Works on all devices
- **Production Ready**: Tested and optimized

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bootstrap 5 for responsive framework
- Font Awesome for icons
- Flask for web framework
- All contributors and testers

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Roadmap

- [ ] User authentication system
- [ ] Database integration for progress tracking
- [ ] Real AI detection API integration
- [ ] Mobile app (iOS & Android)
- [ ] Multi-language support
- [ ] Admin dashboard
- [ ] Analytics and reporting

## Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ for online safety and scam awareness**

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** March 12, 2026