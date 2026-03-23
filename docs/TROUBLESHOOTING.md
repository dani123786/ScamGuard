# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "Page Not Found" Error

**Symptoms:**
- Browser shows "404 Not Found" or "Page Not Found"
- URLs don't work

**Solutions:**

1. **Make sure the Flask server is running:**
   ```bash
   python app.py
   ```
   You should see:
   ```
   * Running on http://127.0.0.1:5000
   ```

2. **Use the correct URL:**
   - Correct: `http://localhost:5000` or `http://127.0.0.1:5000`
   - Wrong: `http://localhost:5000/index.html`
   - Wrong: Opening HTML files directly in browser

3. **Check if port 5000 is already in use:**
   - Windows: `netstat -ano | findstr :5000`
   - Linux/Mac: `lsof -i :5000`
   
   If port is in use, either:
   - Stop the other application
   - Or change the port in `app.py`:
     ```python
     if __name__ == '__main__':
         app.run(debug=True, port=5001)  # Use different port
     ```

### Issue 2: CSS Errors in awareness.html

**Symptoms:**
- CSS property value expected errors
- Styling issues on awareness page

**Solution:**
This has been fixed! The inline style with Jinja2 variable was removed. If you still see errors:

1. Make sure you have the latest version of `templates/awareness.html`
2. Clear your browser cache (Ctrl+F5)
3. Restart the Flask server

### Issue 3: Module Not Found Error

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
pip install -r requirements.txt
```

Or install Flask directly:
```bash
pip install Flask
```

### Issue 4: Python Not Found

**Symptoms:**
```
'python' is not recognized as an internal or external command
```

**Solutions:**

1. **Install Python:**
   - Download from https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Try using `python3` instead:**
   ```bash
   python3 app.py
   ```

3. **Verify Python installation:**
   ```bash
   python --version
   ```

### Issue 5: Port Already in Use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

1. **Find and kill the process using port 5000:**
   
   Windows:
   ```bash
   netstat -ano | findstr :5000
   taskkill /PID <PID_NUMBER> /F
   ```
   
   Linux/Mac:
   ```bash
   lsof -i :5000
   kill -9 <PID>
   ```

2. **Use a different port:**
   Edit `app.py` and change:
   ```python
   app.run(debug=True, port=5001)
   ```

### Issue 6: Templates Not Found

**Symptoms:**
```
jinja2.exceptions.TemplateNotFound: index.html
```

**Solution:**

1. **Verify folder structure:**
   ```
   ScamShield-Kiro/
   ├── app.py
   ├── templates/
   │   ├── base.html
   │   ├── index.html
   │   ├── awareness.html
   │   └── ...
   └── static/
       └── css/
           └── style.css
   ```

2. **Make sure you're running from the correct directory:**
   ```bash
   cd ScamShield-Kiro
   python app.py
   ```

### Issue 7: Static Files Not Loading

**Symptoms:**
- No CSS styling
- Icons not showing
- Images not loading

**Solutions:**

1. **Check folder structure:**
   ```
   static/
   └── css/
       └── style.css
   ```

2. **Clear browser cache:**
   - Chrome/Edge: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Or use Ctrl+F5 to hard refresh

3. **Check Flask static folder configuration:**
   In `app.py`, make sure:
   ```python
   app = Flask(__name__)  # This automatically sets static folder
   ```

### Issue 8: File Upload Not Working (AI Detector)

**Symptoms:**
- Can't upload files
- Upload button doesn't work

**Solutions:**

1. **Check file size:**
   - Default max size is 16MB
   - For larger files, modify `config.py`

2. **Check file format:**
   - Images: PNG, JPG, JPEG, GIF, WebP
   - Audio: MP3, WAV, OGG, M4A
   - Video: MP4, WebM, AVI, MOV

3. **Check browser console for errors:**
   - Press F12 to open developer tools
   - Check Console tab for JavaScript errors

### Issue 9: Quiz Not Loading

**Symptoms:**
- Quiz questions don't appear
- Start button doesn't work

**Solutions:**

1. **Check browser console:**
   - Press F12
   - Look for JavaScript errors

2. **Verify API endpoint:**
   - Open: `http://localhost:5000/api/quiz/questions`
   - Should return JSON with questions

3. **Clear browser cache and reload**

### Issue 10: Scam Checker Not Working

**Symptoms:**
- Analysis doesn't run
- No results shown

**Solutions:**

1. **Check if content is entered:**
   - Make sure you've pasted content in the text area

2. **Check browser console for errors:**
   - Press F12
   - Look for network errors

3. **Verify API endpoint:**
   - Should POST to `/api/check`

## Quick Fixes

### Reset Everything
```bash
# Stop the server (Ctrl+C)
# Clear browser cache
# Restart the server
python app.py
```

### Reinstall Dependencies
```bash
pip uninstall flask
pip install -r requirements.txt
```

### Check Python Version
```bash
python --version
# Should be 3.7 or higher
```

## Getting Help

If none of these solutions work:

1. **Check the error message carefully**
2. **Look at the terminal/console output**
3. **Check browser developer console (F12)**
4. **Verify all files are in correct locations**
5. **Make sure you're using the correct URL**

## Useful Commands

### Start the application:
```bash
# Windows
python app.py
# or
run.bat

# Linux/Mac
python3 app.py
# or
bash run.sh
```

### Check if server is running:
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

### Test if Flask is installed:
```bash
python -c "import flask; print(flask.__version__)"
```

### View all routes:
Add this to `app.py` temporarily:
```python
@app.route('/routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        output.append(str(rule))
    return '<br>'.join(output)
```

Then visit: `http://localhost:5000/routes`

## Still Having Issues?

Make sure:
- ✅ Python 3.7+ is installed
- ✅ Flask is installed (`pip install flask`)
- ✅ You're in the correct directory
- ✅ Server is running (`python app.py`)
- ✅ Using correct URL (`http://localhost:5000`)
- ✅ All template files exist in `templates/` folder
- ✅ CSS file exists in `static/css/` folder

---

**Remember:** Always run `python app.py` from the project root directory!