@echo off
echo ========================================
echo     ScamGuard - Starting Application
echo ========================================

:: Keys are loaded from .env file automatically
:: Make sure .env file exists with your credentials

echo.
echo [+] Starting Flask app...
echo [+] Open browser at: http://127.0.0.1:5000
echo.

python app.py

pause