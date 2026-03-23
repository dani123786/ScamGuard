# 🚀 Deployment Guide

## Vercel Deployment (Recommended)

### Prerequisites
- GitHub account
- Vercel account (free)

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/scamguard.git
git push -u origin main
```

2. **Deploy on Vercel**
- Go to [vercel.com](https://vercel.com)
- Click "New Project"
- Import your GitHub repository
- Vercel will auto-detect Flask
- Click "Deploy"

3. **Done!**
Your app will be live at: `https://your-project.vercel.app`

### Environment Variables (Optional)
If using email notifications:
- Add `SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`, `SENDER_PASSWORD` in Vercel dashboard

---

## Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed

### Steps

1. **Create Procfile**
```
web: gunicorn app:app
```

2. **Add gunicorn to requirements.txt**
```bash
echo "gunicorn==20.1.0" >> requirements.txt
```

3. **Deploy**
```bash
heroku login
heroku create your-app-name
git push heroku main
heroku open
```

---

## PythonAnywhere Deployment

### Steps

1. **Upload files** to PythonAnywhere
2. **Create virtual environment**
```bash
mkvirtualenv --python=/usr/bin/python3.8 scamguard
pip install -r requirements.txt
```

3. **Configure WSGI file**
```python
import sys
path = '/home/yourusername/scamguard'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

4. **Reload web app** in dashboard

---

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Build and Run
```bash
docker build -t scamguard .
docker run -p 5000:5000 scamguard
```

---

## Environment Variables

### Required
None (app works without configuration)

### Optional (for email reports)
- `SMTP_SERVER`: SMTP server address
- `SMTP_PORT`: SMTP port (usually 587)
- `SENDER_EMAIL`: Sender email address
- `SENDER_PASSWORD`: Email password or app password
- `AUTHORITY_EMAILS`: Comma-separated list of authority emails

---

## Post-Deployment Checklist

- [ ] Test all pages load correctly
- [ ] Verify videos play properly
- [ ] Test quiz functionality
- [ ] Check scam checker tool
- [ ] Test AI detector
- [ ] Verify report submission
- [ ] Test on mobile devices
- [ ] Check responsive design
- [ ] Verify all links work
- [ ] Test form submissions

---

## Troubleshooting

### Videos not loading
- Ensure videos are in `static/videos/` folder
- Check file names match exactly
- Verify video format (MP4 recommended)

### Styles not applying
- Clear browser cache
- Check `static/css/style.css` exists
- Verify CSS file is linked in base.html

### Forms not submitting
- Check Flask routes are correct
- Verify CSRF protection if enabled
- Check browser console for errors

---

## Performance Optimization

### For Production
1. Enable caching
2. Compress static files
3. Use CDN for Bootstrap/Font Awesome
4. Optimize images and videos
5. Enable gzip compression

### Vercel Specific
- Vercel automatically handles caching
- Static files served from CDN
- Automatic HTTPS
- Global edge network

---

## Monitoring

### Recommended Tools
- Vercel Analytics (built-in)
- Google Analytics
- Sentry for error tracking
- Uptime monitoring (UptimeRobot)

---

## Scaling

### Horizontal Scaling
- Vercel handles automatically
- No configuration needed

### Database (Future)
- Add PostgreSQL for user data
- Use Redis for caching
- Implement session management

---

**Need help?** Open an issue on GitHub!