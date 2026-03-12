# 🚀 Quick Start Guide - ScamGuard

## Start Your System in 3 Steps

### Step 1: Install Dependencies (First time only)
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Open in Browser
```
http://127.0.0.1:5000
```

---

## ✅ What's Working

### All 10 Videos Are Live! 🎉
1. Phishing Scams
2. Cryptocurrency Scams
3. Investment & Ponzi Schemes
4. Tech Support Scams
5. E-Commerce & Shopping Scams
6. Identity Theft & Data Breach
7. Lottery & Prize Scams
8. Employment & Job Scams
9. Social Media & Impersonation
10. Deepfake Scams

### All Features Active
- ✅ Educational videos on all scam pages
- ✅ Interactive practice quizzes (10 questions per scam)
- ✅ Main quiz with 3 difficulty levels
- ✅ Scam checker tool
- ✅ AI content detector
- ✅ Report system

---

## 📱 Main Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Landing page |
| Awareness | `/awareness` | All 10 scam types |
| Scam Details | `/awareness/phishing` | Individual scam pages with videos |
| Quiz | `/quiz` | Main quiz (easy/medium/hard) |
| Checker | `/checker` | Analyze emails, URLs, messages |
| AI Detector | `/ai-detector` | Detect AI-generated content |
| Report | `/report` | Report scams to authorities |
| Resources | `/resources` | Additional materials |

---

## 🎬 Video Examples

Visit any scam detail page to see videos:
- `http://127.0.0.1:5000/awareness/phishing`
- `http://127.0.0.1:5000/awareness/cryptocurrency`
- `http://127.0.0.1:5000/awareness/deepfake`
- etc.

---

## 🛠️ Troubleshooting

### Videos not showing?
- Check that files are in `static/videos/` folder
- Verify filenames match exactly (lowercase, underscores)
- Clear browser cache

### Port already in use?
```bash
# Change port in app.py (last line):
app.run(debug=True, port=5001)
```

### Dependencies missing?
```bash
pip install flask
```

---

## 📁 Important Files

- `app.py` - Main application
- `static/videos/` - All 10 video files
- `templates/` - HTML pages
- `reports/` - Saved scam reports
- `requirements.txt` - Dependencies

---

## 🎯 System Status

**Status:** ✅ FULLY OPERATIONAL  
**Videos:** 10/10 Complete  
**Features:** All Active  
**Ready for:** Production Use

---

**Need help?** Check `SYSTEM_READY.md` for detailed documentation.
