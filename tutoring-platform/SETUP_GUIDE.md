# 🚀 Quick Setup Guide

## Prerequisites Installation

### 1. Install Required Software

**macOS:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python, Node.js, PostgreSQL, Redis
brew install python@3.11 node postgresql@16 redis

# Start services
brew services start postgresql@16
brew services start redis
```

**Windows:**
- Install Python 3.11 from https://python.org
- Install Node.js 20 from https://nodejs.org
- Install PostgreSQL 16 from https://postgresql.org
- Install Redis from https://github.com/microsoftarchive/redis/releases

**Linux (Ubuntu/Debian):**
```bash
# Update packages
sudo apt update

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
sudo apt install postgresql-16 postgresql-contrib

# Install Redis
sudo apt install redis-server
```

## Quick Start (Docker - Recommended)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd tutoring-platform
cp backend/.env.example backend/.env
```

### 2. Configure Environment
Edit `backend/.env` with your settings:
- Set a secure `SECRET_KEY`
- Configure email settings (SendGrid)
- Configure Stripe keys
- Other API keys as needed

### 3. Start Everything
```bash
# Build and start all services
docker-compose up -d

# Wait for services to start, then run migrations
docker-compose exec backend python manage.py migrate

# Create admin user
docker-compose exec backend python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec backend python manage.py loaddata fixtures/initial_data.json
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs

## Manual Setup (Without Docker)

### Backend Setup

1. **Create and activate virtual environment**
```bash
cd backend
python3 -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create PostgreSQL database**
```bash
# macOS/Linux:
createdb tutoring_db

# Or via psql:
psql postgres
CREATE DATABASE tutoring_db;
CREATE USER tutoring_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE tutoring_db TO tutoring_user;
\q
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Start Django server**
```bash
python manage.py runserver
```

8. **Start Celery (new terminal)**
```bash
# Activate venv first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start worker
celery -A tutoring worker -l info

# Start beat (new terminal, venv activated)
celery -A tutoring beat -l info
```

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start development server**
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## Initial Data Setup

### Via Django Admin (http://localhost:8000/admin)

1. **Create Subjects**
   - Go to Core > Subjects
   - Add: Physics, Mathematics, English Literature, General Science
   - Set icons, colors, descriptions

2. **Add Topics**
   - For each subject, add relevant topics
   - Set curriculum (NCEA/Cambridge) and year levels

3. **Configure Pricing Tiers**
   - Go to Core > Pricing Tiers
   - Add tiers for different year levels:
     * Year 9-10: $65/hr
     * NCEA Level 1 / Cambridge IGCSE: $70/hr
     * NCEA Level 2-3 / Cambridge AS: $75/hr
     * Cambridge A2: $80/hr

4. **Set Up Packages**
   - Go to Finances > Packages
   - Add standard packages (5, 10, 20, 30 sessions)
   - Set discounts (3%, 5%, 10%, 15%)

5. **Configure Email Templates**
   - Go to Communications > Email Templates
   - Create templates for:
     * Booking confirmation
     * Session reminders
     * Invoice
     * Payment receipt
     * Progress report

6. **Update Site Settings**
   - Go to Core > Site Settings
   - Set business hours, contact info, policies
   - Configure booking and cancellation policies

7. **Add Testimonials and FAQs**
   - Add client testimonials
   - Add frequently asked questions

### Via API or Custom Commands

Create a management command to seed initial data:

```bash
python manage.py seed_initial_data
```

## Development Workflow

### Backend Development

```bash
# Activate venv
source venv/bin/activate

# Make model changes
# Edit models in apps/*/models.py

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create API endpoints
# Edit serializers.py, views.py, urls.py in each app

# Test API
http://localhost:8000/api/docs/  # Swagger UI
```

### Frontend Development

```bash
# Start dev server (auto-reloads)
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Common Issues & Solutions

### Database Connection Error
```
FATAL:  password authentication failed for user "tutoring_user"
```
**Solution**: Check DATABASE_URL in .env matches PostgreSQL credentials

### Redis Connection Error
```
Error 111 connecting to localhost:6379. Connection refused.
```
**Solution**: Make sure Redis is running
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Or run manually
redis-server
```

### Port Already in Use
```
Error: That port is already in use
```
**Solution**: Kill the process or use a different port
```bash
# Find process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port
python manage.py runserver 8001
```

### Module Not Found
```
ModuleNotFoundError: No module named 'X'
```
**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt  # Backend
npm install                      # Frontend
```

## Next Steps

1. **Customize Content**
   - Update tutor bio in About page
   - Add your qualifications and photo
   - Customize email templates

2. **Configure Integrations**
   - Set up SendGrid for emails
   - Configure Stripe for payments
   - Set up AWS S3 for file storage (optional)

3. **Populate Resources**
   - Upload NCEA past papers
   - Upload Cambridge past papers
   - Create study guides and worksheets

4. **Test Booking Flow**
   - Create a test student account
   - Test booking a session
   - Test email notifications
   - Test payment flow

5. **Deploy**
   - Follow deployment guide in README.md
   - Set up production environment
   - Configure domain and SSL

## Support

For issues or questions:
- Check README.md for detailed documentation
- Review API docs at /api/docs/
- Check Django admin at /admin/

Happy tutoring! 🎓
