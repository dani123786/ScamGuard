-- ScamGuard Supabase Database Setup

-- =========================================================================
-- 1. CREATE admin_users TABLE
-- =========================================================================
CREATE TABLE IF NOT EXISTS admin_users (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  username VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'viewer' CHECK (role IN ('viewer', 'editor', 'admin')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================================
-- 2. INSERT DEFAULT ADMIN USER
-- =========================================================================
-- Credentials: username = "admin", password = "admin123"
INSERT INTO admin_users (username, password_hash, role)
VALUES (
  'admin',
  'pbkdf2:sha256:600000$bUSuVQzEfjZtoZ5c$4d545b46e4b27c61c551c7bb64b1f416efd537d88d89e832027f8d5063c4d320',
  'admin'
)
ON CONFLICT (username) DO NOTHING;

-- =========================================================================
-- 3. CREATE OTHER REQUIRED TABLES (if they don't exist)
-- =========================================================================

-- Reports table (for storing user scam reports)
CREATE TABLE IF NOT EXISTS reports (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  scam_type VARCHAR(100),
  lost_money VARCHAR(10),
  amount VARCHAR(50),
  description TEXT,
  ai_analysis JSONB,
  submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quiz questions table
CREATE TABLE IF NOT EXISTS quiz_questions (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  question_text TEXT NOT NULL,
  option_1 VARCHAR(500),
  option_2 VARCHAR(500),
  option_3 VARCHAR(500),
  option_4 VARCHAR(500),
  correct_answer_index INT,
  explanation TEXT,
  difficulty VARCHAR(50),
  is_active BOOLEAN DEFAULT TRUE,
  correct_count INT DEFAULT 0,
  incorrect_count INT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Scam definitions table
CREATE TABLE IF NOT EXISTS scam_definitions (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  scam_type VARCHAR(100) UNIQUE NOT NULL,
  title VARCHAR(255),
  description TEXT,
  ai_content JSONB,
  view_count INT DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Practice quizzes table
CREATE TABLE IF NOT EXISTS practice_quizzes (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  scam_type VARCHAR(100),
  question_id BIGINT REFERENCES quiz_questions(id) ON DELETE CASCADE,
  completion_count INT DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  action VARCHAR(50),
  table_name VARCHAR(100),
  record_id BIGINT,
  old_values JSONB,
  new_values JSONB,
  changed_by VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================================
-- 4. CREATE INDEXES FOR PERFORMANCE
-- =========================================================================
CREATE INDEX IF NOT EXISTS idx_reports_submitted_at ON reports(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_difficulty ON quiz_questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_scam_definitions_active ON scam_definitions(is_active);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- =========================================================================
-- 5. ENABLE ROW LEVEL SECURITY (Optional but Recommended)
-- =========================================================================
-- Uncomment these if you want to enforce RLS policies:
-- ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE quiz_questions ENABLE ROW LEVEL SECURITY;
-- Note: With Service Role Key, RLS is bypassed, so only enable if needed

-- =========================================================================
-- VERIFICATION QUERIES
-- =========================================================================
-- Run these after setup to verify everything was created:
-- 
-- SELECT * FROM admin_users;
-- SELECT COUNT(*) FROM quiz_questions;
-- SELECT COUNT(*) FROM scam_definitions;
-- SELECT COUNT(*) FROM reports;
