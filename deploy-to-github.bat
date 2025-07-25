@echo off
echo ==================================
echo    رفع المشروع إلى GitHub
echo ==================================

echo.
echo الخطوة 1: إعداد Git repository...
git init

echo.
echo الخطوة 2: إضافة جميع الملفات...
git add .

echo.
echo الخطوة 3: إجراء commit...
git commit -m "Deploy personality test website to Render"

echo.
echo الخطوة 4: ربط المشروع بـ GitHub...
git remote add origin https://github.com/AmiraSayedMohamed/Personality-Test-Website.git

echo.
echo الخطوة 5: رفع الملفات...
git branch -M main
git push -u origin main

echo.
echo ==================================
echo   تم رفع المشروع بنجاح! ✅
echo ==================================
echo.
echo الآن اذهبي إلى:
echo https://render.com
echo وابدئي عملية النشر
echo.
pause
