# دليل نشر الموقع على Render

## خطوات النشر:

### 1. تحضير المشروع:
- تأكد من أن جميع الملفات محفوظة
- تحقق من وجود `requirements_irt.txt` و `package.json`

### 2. إنشاء حساب على Render:
- اذهب إلى [render.com](https://render.com) وأنشئ حساب
- اربط حساب GitHub الخاص بك

### 3. رفع المشروع إلى GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 4. نشر Backend (FastAPI):
1. في Render Dashboard، اضغط "New" → "Web Service"
2. اختر GitHub repository الخاص بك
3. املأ التفاصيل:
   - **Name**: `personality-test-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements_irt.txt`
   - **Start Command**: `python simple_backend.py`
4. في Environment Variables أضف:
   - `PORT`: `10000` (Render يحدد هذا تلقائياً)

### 5. نشر Frontend (React):
1. في Render Dashboard، اضغط "New" → "Web Service"
2. اختر نفس GitHub repository
3. املأ التفاصيل:
   - **Name**: `personality-test-frontend`
   - **Environment**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npx serve -s build -l $PORT`
4. في Environment Variables أضف:
   - `REACT_APP_BACKEND_URL`: رابط Backend الذي حصلت عليه من الخطوة السابقة
   - مثال: `https://personality-test-backend.onrender.com`

### 6. الوصول لصفحة الإدارة:
بعد النشر، يمكنك الوصول لصفحة الإدارة عبر:
```
https://your-frontend-app.onrender.com/admin.html?key=secret_admin_2025
```

### 7. بيانات الدخول للإدارة:
- **اسم المستخدم**: `admin`
- **كلمة المرور**: `admin123`

## ملاحظات مهمة:

### أمان الموقع:
1. **غير المفتاح السري**: في `admin.html` غير `secret_admin_2025` لمفتاح آخر
2. **غير بيانات الإدارة**: في `simple_backend.py` غير `admin/admin123`
3. **استخدم HTTPS**: Render يوفر HTTPS تلقائياً

### رابطة الموقع النهائية:
- **الموقع الرئيسي**: `https://your-frontend-app.onrender.com`
- **صفحة الإدارة**: `https://your-frontend-app.onrender.com/admin.html?key=YOUR_SECRET_KEY`
- **API**: `https://your-backend-app.onrender.com`

### استكشاف الأخطاء:
1. تحقق من logs في Render Dashboard
2. تأكد من أن Backend يعمل قبل Frontend
3. تحقق من Environment Variables
4. تأكد من CORS settings

### تحديثات مستقبلية:
- كل push لـ GitHub سيؤدي لإعادة نشر تلقائي
- يمكنك إيقاف Auto-Deploy من إعدادات الخدمة

## مثال للروابط النهائية:
```
Frontend: https://personality-test-frontend.onrender.com
Backend: https://personality-test-backend.onrender.com
Admin: https://personality-test-frontend.onrender.com/admin.html?key=secret_admin_2025
```
