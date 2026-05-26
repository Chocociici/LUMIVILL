# 🚀 Quick Start Commands for ARMOR Render Deployment

## 🔧 Local Development Setup

```bash
# 1. Navigate to project
cd C:\Users\EAE\ARMOR

# 2. Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup Django
cd app0
python manage.py migrate
python manage.py createsuperuser

# 5. Run Django (Terminal 1)
python manage.py runserver

# 6. Run Chat Server (Terminal 2)
cd ..
python chat_server.py
```

## 📝 Environment Variables for Render

### Web Service (.env)
```
DEBUG=False
SECRET_KEY=<generate-with>: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SETTINGS_MODULE=app0.settings
ALLOWED_HOSTS=armor.onrender.com,yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
PYTHONUNBUFFERED=true
```

### Background Worker (.env)
```
CHAT_PORT=3001
DEBUG=False
PYTHONUNBUFFERED=true
```

## 🚀 Render Configuration

### Web Service Settings
- **Build Command:** `bash build.sh`
- **Start Command:** `cd app0 && daphne -b 0.0.0.0 -p $PORT app0.asgi:application`
- **Plan:** Standard (or appropriate for your needs)

### Background Worker Settings
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python chat_server.py`
- **Plan:** Standard (or appropriate for your needs)

## 🔍 Verification Commands

```bash
# Check imports are correct
grep -r "DJANGO_SETTINGS_MODULE" app0/manage.py app0/app0/wsgi.py app0/app0/asgi.py
# Should show: app0.settings (NOT app0.app0.settings)

# Check settings.py
grep "ROOT_URLCONF\|STATICFILES_STORAGE\|MEDIA_ROOT" app0/app0/settings.py

# Check Procfile
cat Procfile

# Check requirements.txt has whitenoise
grep whitenoise requirements.txt
```

## 📦 Dependencies Check

```bash
# Verify all key packages are installed
pip list | grep -E "Django|channels|daphne|websockets|whitenoise"
```

## 🐛 Troubleshooting

### Check Django imports
```bash
cd app0
python -c "from app0.settings import *; print('✅ Settings import OK')"
```

### Check WebSocket routing
```bash
python -c "from chat.routing import websocket_urlpatterns; print('✅ WebSocket routes OK')"
```

### Check static files
```bash
cd app0
python manage.py collectstatic --noinput --verbosity 2
```

### Check migrations
```bash
cd app0
python manage.py showmigrations
python manage.py migrate
```

## 📊 Post-Deployment on Render

After deployment, run these commands in Web Service shell:

```bash
# Check migrations status
python manage.py showmigrations

# Create superuser
python manage.py createsuperuser

# Check static files
ls -la staticfiles/

# Check media directory
ls -la media/

# Monitor logs
tail -f render.log
```

## 🔐 Generate SECRET_KEY

```python
# Run this locally to generate a strong SECRET_KEY
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())

# Then copy the output and set it in Render environment variables
```

## 🌐 Test WebSocket Connection

```javascript
// Open browser console and test WebSocket
const socket = new WebSocket('wss://your-app.onrender.com/ws/chat/');
socket.onopen = () => console.log('✅ WebSocket connected');
socket.onerror = (e) => console.error('❌ WebSocket error:', e);
socket.onmessage = (e) => console.log('📨 Message:', e.data);
```

## 📋 Files Modified/Created

✅ **Modified:**
- app0/manage.py
- app0/app0/wsgi.py
- app0/app0/asgi.py
- app0/app0/settings.py
- Procfile
- requirements.txt
- .gitignore
- .env.example

✅ **Created:**
- runtime.txt
- build.sh
- render.yaml
- RENDER_DEPLOY.md
- ENVIRONMENT_VARIABLES.md
- DEPLOYMENT_GUIDE.md
- DEPLOYMENT_CHECKLIST.md
- QUICK_START.md (this file)

## ✨ All Done!

Your ARMOR project is ready for Render deployment. Follow the Render Configuration section above to set up your services.

For detailed instructions, see [RENDER_DEPLOY.md](RENDER_DEPLOY.md)
