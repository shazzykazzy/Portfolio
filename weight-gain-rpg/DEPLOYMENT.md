# 🚀 Deployment Guide - Weight Gain RPG

Complete guide for deploying your Weight Gain RPG app to various platforms.

## 📋 Pre-Deployment Checklist

- [ ] Test locally with `./run.sh`
- [ ] Verify all features work
- [ ] Check database is created correctly
- [ ] Test on mobile browser
- [ ] Review security settings
- [ ] Backup any existing data

## 🏠 Local Development

### Quick Start
```bash
./run.sh
```

### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
cd backend
python app.py
```

Access at: `http://localhost:5000`

## 🌐 Production Deployment Options

### Option 1: Heroku (Free/Paid)

**Pros:** Easy, Git-based, automatic SSL
**Cons:** Dyno sleep on free tier

#### Steps:

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Login**
```bash
heroku login
```

3. **Create app**
```bash
heroku create weight-gain-rpg
```

4. **Create Procfile**
```bash
echo "web: gunicorn backend.app:app" > Procfile
```

5. **Add gunicorn to requirements.txt**
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

6. **Deploy**
```bash
git init
git add .
git commit -m "Initial deploy"
git push heroku main
```

7. **Open app**
```bash
heroku open
```

**Environment Variables:**
```bash
heroku config:set FLASK_ENV=production
```

### Option 2: Railway (Recommended)

**Pros:** Easy, free tier, automatic deployments
**Cons:** Limited free hours

#### Steps:

1. **Visit** [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **New Project** → Deploy from GitHub repo
4. **Select** your repository
5. **Configure:**
   - Start Command: `cd backend && python app.py`
   - Or use Procfile
6. **Deploy** - Automatic!

**Custom Domain:**
- Settings → Domains → Add custom domain
- Configure DNS records

### Option 3: Render

**Pros:** Free tier, easy setup, automatic SSL
**Cons:** Slower cold starts on free tier

#### Steps:

1. **Visit** [render.com](https://render.com)
2. **New Web Service**
3. **Connect** GitHub repository
4. **Configure:**
   - Name: weight-gain-rpg
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && gunicorn app:app`
5. **Deploy**

**Environment Variables:**
```
PYTHON_VERSION=3.11.0
FLASK_ENV=production
```

### Option 4: PythonAnywhere

**Pros:** Free tier, Python-focused, easy for beginners
**Cons:** Limited free resources

#### Steps:

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com)
2. **Upload files** via Files tab
3. **Open Bash console**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. **Web tab** → Add new web app
5. **Configure WSGI file:**
```python
import sys
path = '/home/yourusername/weight-gain-rpg'
if path not in sys.path:
    sys.path.append(path)

from backend.app import app as application
```
6. **Set working directory** to `/home/yourusername/weight-gain-rpg/backend`
7. **Reload** web app

### Option 5: DigitalOcean App Platform

**Pros:** Scalable, professional, good free tier
**Cons:** More complex setup

#### Steps:

1. **Create** DigitalOcean account
2. **App Platform** → Create App
3. **Connect** GitHub repository
4. **Configure:**
   - Type: Web Service
   - Environment: Python
   - HTTP Port: 5000
5. **App Spec:**
```yaml
name: weight-gain-rpg
services:
- name: web
  github:
    repo: yourusername/weight-gain-rpg
    branch: main
  run_command: cd backend && gunicorn app:app -b 0.0.0.0:8080
  environment_slug: python
  instance_size_slug: basic-xxs
  instance_count: 1
```
6. **Deploy**

### Option 6: Docker + VPS

**Pros:** Full control, portable, scalable
**Cons:** Requires server management

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create uploads directory
RUN mkdir -p frontend/static/uploads

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "backend/app.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./database:/app/database
      - ./frontend/static/uploads:/app/frontend/static/uploads
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

#### Deploy to VPS
```bash
# SSH into server
ssh user@your-server.com

# Clone repo
git clone https://github.com/yourusername/weight-gain-rpg.git
cd weight-gain-rpg

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Option 7: Vercel (Frontend) + Railway (Backend)

**Pros:** Best performance, edge deployment
**Cons:** More complex, requires splitting

#### Steps:

1. **Split project:**
   - Frontend: Deploy to Vercel
   - Backend: Deploy to Railway

2. **Update API calls:**
```javascript
const API_URL = 'https://your-railway-backend.up.railway.app';
```

3. **Configure CORS:**
```python
CORS(app, origins=['https://your-vercel-frontend.vercel.app'])
```

## 🔒 Security Considerations

### Production Settings

1. **Disable Debug Mode**
```python
# In app.py
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. **Secret Key**
```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
```

3. **CORS Configuration**
```python
from flask_cors import CORS
CORS(app, origins=['https://yourdomain.com'])
```

4. **Rate Limiting**
```python
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])
```

5. **HTTPS Enforcement**
Most platforms provide automatic HTTPS. If self-hosting:
```python
from flask_talisman import Talisman
Talisman(app, force_https=True)
```

### Environment Variables
Create `.env` file (don't commit!):
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
DATABASE_URL=path/to/database.db
ALLOWED_ORIGINS=https://yourdomain.com
```

Load in app:
```python
from dotenv import load_dotenv
load_dotenv()
```

## 📊 Database Considerations

### SQLite (Default)
- **Good for:** Single user, small scale
- **Pros:** Simple, no setup
- **Cons:** Not suitable for high traffic

### PostgreSQL (Recommended for Production)
```bash
pip install psycopg2-binary
```

Update database.py:
```python
import os
db_url = os.environ.get('DATABASE_URL', 'sqlite:///database/weight_gain_rpg.db')
```

Most platforms offer free PostgreSQL:
- Heroku: Heroku Postgres
- Railway: Built-in PostgreSQL
- Render: PostgreSQL
- DigitalOcean: Managed Databases

## 📈 Performance Optimization

### Production Optimizations

1. **Gunicorn Workers**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 backend.app:app
```

2. **Static File Caching**
```python
@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response
```

3. **Compress Responses**
```python
from flask_compress import Compress
Compress(app)
```

4. **CDN for Static Assets**
Use Cloudflare, AWS CloudFront, or similar

### Database Optimization
```python
# Add indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON weight_logs(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_date ON weight_logs(log_date)')
```

## 🔍 Monitoring & Logging

### Basic Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/weight', methods=['POST'])
def log_weight():
    logger.info(f"Weight logged: {weight}kg")
    # ... rest of code
```

### Error Tracking
Use Sentry for production error tracking:
```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()]
)
```

### Health Check Endpoint
```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

## 🔄 Backup Strategy

### Automated Database Backups
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp database/weight_gain_rpg.db "backups/backup_$DATE.db"
find backups/ -mtime +30 -delete  # Delete backups older than 30 days
```

Cron job:
```bash
0 2 * * * /path/to/backup.sh
```

### Cloud Storage
Upload backups to S3, Google Cloud Storage, or Dropbox

## 📱 PWA Deployment

### Add Service Worker
Create `frontend/static/sw.js`:
```javascript
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('v1').then((cache) => {
            return cache.addAll([
                '/',
                '/static/css/main.css',
                '/static/js/app.js',
            ]);
        })
    );
});
```

### Add Manifest
Create `frontend/static/manifest.json`:
```json
{
  "name": "Weight Gain RPG",
  "short_name": "Gain RPG",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0F172A",
  "theme_color": "#7C3AED",
  "icons": [
    {
      "src": "/static/images/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/images/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

## 🌍 Custom Domain Setup

### DNS Configuration
Point your domain to deployment:

**A Record:**
```
@ → deployment-ip-address
```

**CNAME:**
```
www → your-app.platform.com
```

### SSL Certificate
Most platforms provide automatic SSL. For self-hosted:
```bash
# Using Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find process
lsof -i :5000
# Kill process
kill -9 <PID>
```

**Database Locked:**
```python
# Increase timeout
conn = sqlite3.connect('database.db', timeout=10)
```

**Memory Issues:**
```bash
# Reduce Gunicorn workers
gunicorn -w 2 backend.app:app
```

**CORS Errors:**
```python
# Allow all origins (dev only!)
CORS(app, origins='*')
```

## 📊 Analytics Integration

### Google Analytics
Add to `index.html`:
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🎯 Post-Deployment Checklist

- [ ] Test all features on production
- [ ] Verify database is working
- [ ] Check mobile responsiveness
- [ ] Test photo uploads
- [ ] Verify XP and achievements
- [ ] Check chart rendering
- [ ] Test on multiple browsers
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Update DNS records
- [ ] Enable SSL
- [ ] Test API endpoints
- [ ] Check error logging
- [ ] Set up analytics
- [ ] Test notifications

## 📚 Resources

- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Heroku Python](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Docker Docs](https://docs.docker.com/)

---

**Ready to deploy! Let's get your Weight Gain RPG live! 🚀**
