# Configuration file for Scam Awareness System

# Application Settings
DEBUG_MODE = True
SECRET_KEY = 'your-secret-key-here-change-in-production'
HOST = '0.0.0.0'
PORT = 5000

# Feature Flags
ENABLE_AI_DETECTOR = True
ENABLE_SCAM_CHECKER = True
ENABLE_QUIZ = True
ENABLE_REPORTING = True

# Risk Score Thresholds
RISK_THRESHOLD_HIGH = 70
RISK_THRESHOLD_MEDIUM = 40

# File Upload Settings (for AI Detector)
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'avi', 'mov', 'mkv'}

# Quiz Settings
QUIZ_PASSING_SCORE = 70  # Percentage
QUIZ_TIME_LIMIT = None  # None for no limit, or seconds

# UI Customization
SITE_NAME = 'ScamGuard'
SITE_TAGLINE = 'Online Scam Awareness System'
PRIMARY_COLOR = '#667eea'
SECONDARY_COLOR = '#764ba2'

# External Links (for Resources page)
EXTERNAL_RESOURCES = {
    'ftc': 'https://reportfraud.ftc.gov',
    'ic3': 'https://www.ic3.gov',
    'ncsc': 'https://www.ncsc.gov.uk',
    'cfpb': 'https://www.consumerfinance.gov'
}

# Email Settings (for future email notifications)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = ''
SMTP_PASSWORD = ''
ADMIN_EMAIL = 'admin@example.com'

# Database Settings (for future database integration)
DATABASE_URI = 'sqlite:///scam_awareness.db'
DATABASE_TRACK_MODIFICATIONS = False

# Analytics (for future integration)
ENABLE_ANALYTICS = False
GOOGLE_ANALYTICS_ID = ''

# Rate Limiting (for future implementation)
RATE_LIMIT_ENABLED = False
RATE_LIMIT_PER_MINUTE = 60

# Cache Settings
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'scam_awareness.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Security Headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'SAMEORIGIN',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
}

# API Keys (for future AI detection API integration)
# Replace with actual API keys when integrating real AI detection services
AI_DETECTION_API_KEY = ''
AI_DETECTION_API_ENDPOINT = ''

# Scam Detection Keywords (can be customized)
SCAM_KEYWORDS = {
    'urgent': ['urgent', 'act now', 'immediate action', 'expires', 'limited time'],
    'financial': ['bank account', 'credit card', 'ssn', 'social security', 'password'],
    'crypto': ['bitcoin', 'crypto', 'wallet', 'seed phrase', 'private key'],
    'prize': ['congratulations', 'winner', 'prize', 'lottery', 'claim now'],
    'trust': ['trust me', 'believe me', 'promise', 'guaranteed', '100%'],
    'emergency': ['emergency', 'hospital', 'accident', 'arrested', 'urgent help']
}

# Content Moderation
ENABLE_CONTENT_MODERATION = False
BLOCKED_WORDS = []  # Add words to block if needed

# Maintenance Mode
MAINTENANCE_MODE = False
MAINTENANCE_MESSAGE = 'System is currently under maintenance. Please check back later.'

# Feature Announcements
SHOW_ANNOUNCEMENTS = True
ANNOUNCEMENTS = [
    {
        'title': 'New AI Detector Feature!',
        'message': 'Now you can detect AI-generated images, videos, and audio.',
        'type': 'info',
        'active': True
    }
]

# Social Media Links (for footer)
SOCIAL_MEDIA = {
    'twitter': '',
    'facebook': '',
    'linkedin': '',
    'github': 'https://github.com/yourusername/scam-awareness-system'
}

# Localization
DEFAULT_LANGUAGE = 'en'
SUPPORTED_LANGUAGES = ['en']  # Add more as you implement translations

# Performance
ENABLE_COMPRESSION = True
MINIFY_HTML = False

# Development Settings
RELOAD_ON_CHANGE = True
SHOW_DEBUG_TOOLBAR = False
