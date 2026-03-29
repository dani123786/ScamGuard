# ScamGuard Website Issues Analysis & Solutions

## Overview
Your Flask application has **database connection issues** and **access control problems** that affect different sections of the site. Below is a detailed breakdown and solutions.

---

## 🔴 CRITICAL ISSUES IDENTIFIED

### 1. **Supabase Database Connection Issue**

**Problem:**
- The `.env` file uses `SUPABASE_KEY` (anonymous key) instead of `SUPABASE_SERVICE_ROLE_KEY` (service role key)
- The app expects `SUPABASE_SERVICE_ROLE_KEY` as the FIRST priority, then falls back to `SUPABASE_KEY`
- The anonymous key has LIMITED permissions and may not have access to the `admin_users` table
- **Result:** Admin authentication fails because the app can't read from the `admin_users` table

**Current Configuration (in `.env`):**
```
SUPABASE_URL=https://zxtyyylzrazcipyaxssf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (ANONYMOUS KEY)
```

**Why Some Sections Work & Others Don't:**
- ✅ **PUBLIC routes work:** `/`, `/awareness`, `/quiz`, `/checker`, `/report` → These don't require auth
- ✅ **Public API endpoints work:** These use fallback data or cache when DB isn't available
- ❌ **ADMIN routes fail:** `/admin/login`, `/admin/reports`, `/admin/quiz-questions` → Need authentication via `admin_users` table
- ❌ **Admin API calls fail:** Content management, analytics, imports/exports → All require database access with proper permissions

---

### 2. **Authentication Module Issues**

**Problem:**
```python
# In app.py (lines 105-120)
ext._AUTH_AVAILABLE = True/False  # Flag set during initialization
ext.require_auth = require_auth    # Auth decorators assigned
```

If the database connection fails during startup:
- `login_user()` function returns `None` (cannot query `admin_users` table)
- Users cannot log in to admin panel
- Protected routes return **401 Unauthorized** or redirect to login page

**Dev Fallback:**
- There's a hardcoded fallback: username `admin`, password `admin123`
- BUT it's disabled by default (requires `SCAMGUARD_DEV_FALLBACK=1` environment variable)
- Currently NOT set in `.env`, so this fallback is unavailable

---

### 3. **Missing Supabase Tables**

Your Supabase database MUST have these tables for the app to function:

| Table Name | Purpose | Status |
|-----------|---------|--------|
| `admin_users` | Store admin login credentials | ❌ Likely missing |
| `reports` | Store user scam reports | ✓ Probably exists |
| `quiz_questions` | Store quiz questions | ⚠️ May exist but empty |
| `scam_definitions` | Scam type information | ⚠️ May exist but empty |
| `practice_quizzes` | Practice quiz content | ⚠️ May exist but empty |
| `audit_logs` | Log admin actions | ⚠️ May exist but empty |

---

## ✅ RECOMMENDED SOLUTIONS

### **Solution 1: Get Service Role Key from Supabase (BEST)**

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project: **zxtyyylzrazcipyaxssf**
3. Navigate to: **Project Settings → API → Service Role Key**
4. Copy the **Service Role Key** (NOT the anon key)
5. Update `.env`:
```bash
SUPABASE_URL=https://zxtyyylzrazcipyaxssf.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (SERVICE ROLE KEY - LONG STRING)
```

### **Solution 2: Create admin_users Table in Supabase**

1. In Supabase Dashboard, go to **SQL Editor**
2. Run this SQL to create the table:
```sql
CREATE TABLE IF NOT EXISTS admin_users (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  username VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'viewer' CHECK (role IN ('viewer', 'editor', 'admin')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add sample admin user (password: admin123)
INSERT INTO admin_users (username, password_hash, role) VALUES
  ('admin', 'pbkdf2:sha256:600000$abcd1234...', 'admin'); -- Use generate_password_hash from werkzeug
```

3. To generate the correct password hash, run in Python:
```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('admin123', method='pbkdf2:sha256'))
```

### **Solution 3: Enable Dev Fallback (TEMPORARY)**

If you need to test immediately, add to `.env`:
```bash
SCAMGUARD_DEV_FALLBACK=1
```
Then use credentials:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **NOT for production** — Only for testing/development

---

## 🔧 STEP-BY-STEP FIX

### **Priority 1: Fix Database Credentials**
1. Update `.env` with Service Role Key from Supabase
2. Restart the application: `python app.py`
3. Check startup logs for messages like `[+] Supabase connected successfully`

### **Priority 2: Create admin_users Table**
1. Log into Supabase
2. Create the `admin_users` table (see SQL above)
3. Add at least one admin user

### **Priority 3: Test Access**
1. Navigate to `http://localhost:5000/admin/login`
2. Enter admin credentials
3. You should see the admin dashboard

### **Priority 4: Populate Other Tables** (if needed)
1. Create remaining tables in Supabase for quiz questions, scam definitions, etc.
2. Use the admin interface to add content

---

## 🧪 VERIFICATION CHECKLIST

After making changes:

- [ ] Supabase Service Role Key is in `.env`
- [ ] Application starts with `[+] Supabase connected successfully` message
- [ ] `admin_users` table exists in Supabase
- [ ] Can log in to `/admin/login` with valid credentials
- [ ] Admin dashboard loads at `/admin/reports`
- [ ] Can manage quiz questions at `/admin/quiz-questions`
- [ ] Can view analytics at `/admin/analytics`
- [ ] Public pages still work: `/`, `/awareness`, `/quiz`, `/checker`

---

## 📋 CURRENT ACCESS CONTROL STATUS

### Public Routes (No Auth Required) ✅
```
GET  /                          # Homepage
GET  /awareness                 # Scam awareness page
GET  /awareness/<scam_type>     # Scam details
GET  /quiz                      # Quiz page
GET  /checker                   # Scam checker page
GET  /verify                    # Verification page
GET  /resources                 # Resources page
GET  /report                    # Report page
GET  /api/check-content         # API: Check content
GET  /api/check-url             # API: Check URL
POST /api/submit-report         # API: Submit report
```

### Protected Routes (Auth Required) 🔐
```
GET  /admin/login               # Login page
POST /admin/auth/login          # Login endpoint
POST /admin/auth/logout         # Logout endpoint
GET  /admin/auth/me             # Get current user
GET  /admin/auth/csrf-token     # Get CSRF token (fixed: now requires auth)

GET  /admin/reports             # View all reports
GET  /admin/quiz-questions      # List quiz questions
POST /admin/quiz-questions      # Create question (role: editor, admin)
PUT  /admin/quiz-questions/<id> # Update question (role: editor, admin)

GET  /admin/analytics           # View analytics
POST /admin/import              # Import data (role: admin only)
```

---

## 🛠️ FILES TO MODIFY

1. **`.env`** — Update Supabase credentials
2. **Supabase SQL** — Create `admin_users` table and add user
3. **No code changes needed** — The issue is configuration, not code

---

## 📞 ADDITIONAL NOTES

- **Rate Limiting:** Flask-Limiter is enabled to prevent abuse
- **Cache:** SimpleCacheManager handles caching for quiz questions and scam definitions
- **Audit Logging:** Admin actions are logged if audit_logger initializes
- **Session Timeout:** Admin sessions timeout after 30 minutes of inactivity
- **CSRF Protection:** Protected for admin forms

---

## 🚨 IMPORTANT SECURITY NOTES

1. **Never use anonymous key (`SUPABASE_KEY`) for admin operations**
   - It has limited Row Level Security (RLS) permissions
   - Use Service Role Key for backend operations

2. **Change default credentials** (`admin/admin123`)
   - After setting up the first admin user, remove `SCAMGUARD_DEV_FALLBACK=1`
   - Update password in database

3. **Environment variables**
   - Keep `.env` file locally only
   - Use secure environment variables in production
   - Rotate API keys periodically

---

Would you like me to help you implement these fixes?
