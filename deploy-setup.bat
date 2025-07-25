@echo off
echo ================================
echo   Personality Test Deployment
echo ================================
echo.

echo 1. Checking project files...
if exist "requirements_irt.txt" (
    echo ✅ requirements_irt.txt found
) else (
    echo ❌ requirements_irt.txt missing
    pause
    exit
)

if exist "package.json" (
    echo ✅ package.json found
) else (
    echo ❌ package.json missing
    pause
    exit
)

if exist "simple_backend.py" (
    echo ✅ simple_backend.py found
) else (
    echo ❌ simple_backend.py missing
    pause
    exit
)

echo.
echo 2. Initializing Git repository...
git init

echo.
echo 3. Adding all files...
git add .

echo.
echo 4. Creating initial commit...
git commit -m "Initial deployment setup - Personality Test with Arabic/English support"

echo.
echo ================================
echo Setup complete! Next steps:
echo ================================
echo 1. Create a repository on GitHub
echo 2. Run: git remote add origin YOUR_REPO_URL
echo 3. Run: git branch -M main
echo 4. Run: git push -u origin main
echo 5. Go to render.com and deploy!
echo.
echo Full guide available in DEPLOYMENT-GUIDE.md
echo ================================
pause
