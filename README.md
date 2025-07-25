# 🧠 Personality Test - اختبار الشخصية

A bilingual (Arabic/English) personality test application based on the Big Five personality model with IRT (Item Response Theory) adaptive testing.

## ✨ Features

- 🌐 **Bilingual Support**: Full Arabic and English interface
- 👤 **Personalized Questions**: Questions include user's name for better engagement  
- 📊 **Big Five Model**: Based on scientifically validated personality dimensions
- 🎯 **Adaptive Testing**: Uses IRT for more accurate results
- 📈 **Admin Dashboard**: Complete analytics and user management
- 🔒 **Secure Admin Access**: Protected admin panel with authentication
- 📱 **Responsive Design**: Works on all devices

## 🏗️ Architecture

### Frontend (React)
- Modern React application with hooks
- RTL/LTR support for Arabic/English
- Responsive CSS with gradient backgrounds
- Real-time language switching

### Backend (FastAPI)
- RESTful API with FastAPI
- JSON-based data persistence
- IRT-based scoring algorithm
- Admin authentication system

## 🚀 Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
pip install -r requirements_irt.txt
python simple_backend.py
```
Server runs on http://localhost:8005

### Frontend Setup
```bash
npm install
npm start
```
Application runs on http://localhost:3000

## 🌐 Deployment

See detailed deployment guide in `DEPLOYMENT-GUIDE.md`

### Quick Deploy to Render:
1. Push to GitHub
2. Create Backend service with Python environment
3. Create Frontend service with Node environment
4. Set environment variables
5. Deploy!

## 🔐 Admin Access

Access admin panel at: `/admin.html?key=secret_admin_2025`

**Default Credentials:**
- Username: `admin`  
- Password: `admin123`

**⚠️ Change these credentials before production deployment!**

## 📊 Features Overview

### User Experience
- Welcome form with demographic info
- 50 personalized questions (10 per dimension)
- Real-time progress tracking
- Detailed personality report
- Language toggle (Arabic ⇄ English)

### Admin Dashboard
- User session analytics
- Completion rate statistics
- Demographic distribution charts
- Recent participants table
- Real-time data updates

### Personality Dimensions
1. **Openness** - الانفتاح على الخبرة
2. **Conscientiousness** - الضمير/التنظيم  
3. **Extraversion** - الانبساط
4. **Agreeableness** - الطيبة/التوافق
5. **Neuroticism** - العصابية/الاستقرار العاطفي

## 🛠️ Technical Stack

- **Frontend**: React 18, CSS3, HTML5
- **Backend**: FastAPI, Python 3.8+
- **Data**: JSON file storage with auto-save
- **Deployment**: Render.com
- **Analytics**: Custom dashboard with Chart.js-like visualizations

## 📁 Project Structure

```
personality-test/
├── src/                    # React frontend
│   ├── App.js             # Main application component
│   ├── App.css            # Styling and responsive design
│   └── index.js           # React entry point
├── public/
│   ├── index.html         # HTML template
│   └── admin.html         # Admin dashboard
├── simple_backend.py      # FastAPI backend
├── requirements_irt.txt   # Python dependencies
├── package.json          # Node.js dependencies
└── DEPLOYMENT-GUIDE.md   # Deployment instructions
```

## 🔄 Updates & Maintenance

The application auto-saves all data and supports hot reloading during development. For production updates:

1. Make changes locally
2. Test thoroughly  
3. Push to GitHub
4. Render auto-deploys

## 📞 Support

For deployment help or technical issues, refer to:
- `DEPLOYMENT-GUIDE.md` - Complete deployment walkthrough
- `QUICK-DEPLOY.md` - Quick reference commands
- Render dashboard logs for troubleshooting

## 🏆 Credits

Built with modern web technologies and designed for psychological research and self-assessment applications.

---

**🌟 Ready to deploy? Follow the step-by-step guide in `DEPLOYMENT-GUIDE.md`**
