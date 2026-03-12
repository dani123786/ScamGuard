@echo off
echo ========================================
echo   ScamGuard - Online Scam Awareness
echo ========================================
echo.
echo Starting the application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Flask is not installed. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Application is starting...
echo   Open your browser and go to:
echo   http://localhost:5000
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.

python app.py

pause