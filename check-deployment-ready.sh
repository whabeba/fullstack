#!/bin/bash

echo "🔍 فحص جاهزية المشروع للنشر على Render"
echo "============================================="

# التحقق من الملفات المطلوبة
echo "✅ الملفات الأساسية:"
if [ -f "simple_backend.py" ]; then
    echo "   ✓ simple_backend.py موجود"
else
    echo "   ✗ simple_backend.py مفقود"
fi

if [ -f "requirements_irt.txt" ]; then
    echo "   ✓ requirements_irt.txt موجود"
else
    echo "   ✗ requirements_irt.txt مفقود"
fi

if [ -f "package.json" ]; then
    echo "   ✓ package.json موجود"
else
    echo "   ✗ package.json مفقود"
fi

if [ -f "src/App.js" ]; then
    echo "   ✓ src/App.js موجود"
else
    echo "   ✗ src/App.js مفقود"
fi

if [ -f "public/admin.html" ]; then
    echo "   ✓ public/admin.html موجود"
else
    echo "   ✗ public/admin.html مفقود"
fi

echo ""
echo "📊 تفاصيل المشروع:"
echo "   Backend: Python FastAPI"
echo "   Frontend: React"
echo "   Admin Panel: HTML/JavaScript"
echo "   GitHub: https://github.com/AmiraSayedMohamed/Personality-Test-Website.git"

echo ""
echo "🚀 الخطوات التالية:"
echo "1. شغلي deploy-to-github.bat لرفع المشروع"
echo "2. اذهبي إلى render.com"
echo "3. أنشئي Backend service أولاً"
echo "4. ثم Frontend service"
echo "5. احتفظي بالروابط النهائية"

echo ""
echo "🔗 روابط مهمة:"
echo "   Render: https://render.com"
echo "   GitHub Repo: https://github.com/AmiraSayedMohamed/Personality-Test-Website"

echo ""
echo "============================================="
echo "المشروع جاهز للنشر! 🎉"
