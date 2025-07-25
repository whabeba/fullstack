# Quick Deploy Commands

## After creating GitHub repository:

```bash
# Initialize and push to GitHub
git init
git add .
git commit -m "Initial deployment setup"
git remote add origin https://github.com/YOUR_USERNAME/personality-test.git
git branch -M main
git push -u origin main
```

## Render Configuration:

### Backend Service:
```
Name: personality-test-backend
Environment: Python 3
Build Command: pip install -r requirements_irt.txt
Start Command: python simple_backend.py
Environment Variables:
  PORT = 10000
```

### Frontend Service:
```
Name: personality-test-frontend  
Environment: Node
Build Command: npm install && npm run build
Start Command: npx serve -s build -l $PORT
Environment Variables:
  REACT_APP_BACKEND_URL = https://personality-test-backend.onrender.com
```

## Final URLs:
- Website: https://personality-test-frontend.onrender.com
- Admin: https://personality-test-frontend.onrender.com/admin.html?key=secret_admin_2025

## Login:
- Username: admin
- Password: admin123

## Important: Change security settings after deployment!
