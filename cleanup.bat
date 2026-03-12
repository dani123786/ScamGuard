@echo off
echo ========================================
echo ScamGuard Project Cleanup Script
echo ========================================
echo.
echo This will delete unnecessary files and organize your project for deployment.
echo.
pause

python cleanup.py

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Review the changes
echo 2. Run: git init
echo 3. Run: git add .
echo 4. Run: git commit -m "Initial commit"
echo 5. Push to GitHub
echo 6. Deploy on Vercel
echo.
echo See DEPLOYMENT_CHECKLIST.md for detailed steps.
echo.
pause
