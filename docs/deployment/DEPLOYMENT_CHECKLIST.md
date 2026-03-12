# ✅ Deployment Checklist

## Pre-Deployment Steps

### 1. Clean Up Project
- [ ] Run cleanup script: `python cleanup.py`
- [ ] Or manually delete files listed in `CLEANUP_INSTRUCTIONS.md`
- [ ] Verify no duplicate `ScamGuard` folder exists
- [ ] Verify no extra documentation files in root
- [ ] Verify `.gitignore` file exists
- [ ] Verify `vercel.json` file exists

### 2. Verify Files
- [ ] All 10 videos in `static/videos/` folder
- [ ] `app.py` exists and works
- [ ] `requirements.txt` has all dependencies
- [ ] `README.md` is updated
- [ ] All templates in `templates/` folder
- [ ] CSS file in `static/css/style.css`

### 3. Test Locally
- [ ] Run: `python app.py`
- [ ] Open: `http://127.0.0.1:5000`
- [ ] Test all pages load
- [ ] Test videos play
- [ ] Test quiz works
- [ ] Test scam checker
- [ ] Test AI detector
- [ ] Test report submission
- [ ] Test on mobile (optional)

---

## GitHub Setup

### 1. Initialize Git
```bash
git init
```

### 2. Add Files
```bash
git add .
```

### 3. Commit
```bash
git commit -m "Initial commit - ScamGuard v1.0"
```

### 4. Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name: `scamguard` (or your preferred name)
4. Description: "Online Scam Awareness System"
5. Public or Private (your choice)
6. Don't initialize with README (we already have one)
7. Click "Create repository"

### 5. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/scamguard.git
git branch -M main
git push -u origin main
```

---

## Vercel Deployment

### 1. Sign Up/Login
- [ ] Go to [vercel.com](https://vercel.com)
- [ ] Sign in with GitHub account

### 2. Import Project
- [ ] Click "New Project"
- [ ] Select your GitHub repository
- [ ] Click "Import"

### 3. Configure Project
- [ ] Project Name: `scamguard` (or your choice)
- [ ] Framework Preset: Other (Vercel will auto-detect)
- [ ] Root Directory: `./`
- [ ] Build Command: (leave empty)
- [ ] Output Directory: (leave empty)
- [ ] Install Command: `pip install -r requirements.txt`

### 4. Environment Variables (Optional)
If using email notifications:
- [ ] Add `SMTP_SERVER`
- [ ] Add `SMTP_PORT`
- [ ] Add `SENDER_EMAIL`
- [ ] Add `SENDER_PASSWORD`

### 5. Deploy
- [ ] Click "Deploy"
- [ ] Wait for deployment (2-3 minutes)
- [ ] Get your live URL: `https://your-project.vercel.app`

---

## Post-Deployment Testing

### 1. Test Live Site
- [ ] Visit your Vercel URL
- [ ] Test home page loads
- [ ] Test all navigation links
- [ ] Test awareness page
- [ ] Test individual scam pages
- [ ] Test videos play
- [ ] Test quiz functionality
- [ ] Test scam checker
- [ ] Test AI detector
- [ ] Test report submission

### 2. Test Responsive Design
- [ ] Test on desktop browser
- [ ] Test on tablet (or browser DevTools)
- [ ] Test on mobile phone
- [ ] Test sidebar toggle
- [ ] Test all buttons work
- [ ] Test forms submit correctly

### 3. Performance Check
- [ ] Page load speed acceptable
- [ ] Videos load and play smoothly
- [ ] No console errors
- [ ] All images load
- [ ] CSS styles apply correctly

---

## Troubleshooting

### Videos Not Loading
**Problem:** Videos don't play on deployed site
**Solution:** 
- Ensure videos are in `static/videos/` folder
- Check file names match exactly (case-sensitive)
- Verify videos are pushed to GitHub
- Check Vercel build logs

### Styles Not Applying
**Problem:** Website looks unstyled
**Solution:**
- Verify `static/css/style.css` exists
- Check file is linked in `base.html`
- Clear browser cache
- Check Vercel build logs

### 404 Errors
**Problem:** Some pages show 404
**Solution:**
- Verify all routes in `app.py`
- Check template files exist
- Verify `vercel.json` configuration
- Redeploy if needed

### Build Fails
**Problem:** Vercel build fails
**Solution:**
- Check `requirements.txt` is correct
- Verify Python version compatibility
- Check Vercel build logs for errors
- Ensure `vercel.json` is correct

---

## Optional Enhancements

### Custom Domain
- [ ] Purchase domain (optional)
- [ ] Add domain in Vercel dashboard
- [ ] Configure DNS settings
- [ ] Wait for SSL certificate

### Analytics
- [ ] Enable Vercel Analytics
- [ ] Add Google Analytics (optional)
- [ ] Set up error tracking (Sentry)

### Monitoring
- [ ] Set up uptime monitoring
- [ ] Configure alerts
- [ ] Monitor performance

---

## Final Checklist

- [ ] ✅ Project cleaned up
- [ ] ✅ Pushed to GitHub
- [ ] ✅ Deployed on Vercel
- [ ] ✅ Live site tested
- [ ] ✅ All features working
- [ ] ✅ Responsive on all devices
- [ ] ✅ No errors in console
- [ ] ✅ Videos playing correctly
- [ ] ✅ Forms submitting properly

---

## Success! 🎉

Your ScamGuard application is now live and accessible worldwide!

**Share your URL:**
- `https://your-project.vercel.app`

**Update README.md** with your live URL

**Promote your project:**
- Share on social media
- Add to your portfolio
- Submit to project showcases

---

## Maintenance

### Regular Updates
- Update scam information regularly
- Add new scam types as they emerge
- Update videos periodically
- Monitor user reports

### Git Workflow
```bash
# Make changes
git add .
git commit -m "Description of changes"
git push

# Vercel will auto-deploy!
```

---

**Congratulations on deploying ScamGuard!** 🚀
