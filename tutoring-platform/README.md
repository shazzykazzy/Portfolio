# 🎓 Professional Tutoring Platform - NCEA & Cambridge

A comprehensive, full-stack tutoring management platform for NCEA and Cambridge secondary school students. Built with Django REST Framework and React with TypeScript.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Business Features](#business-features)

## 🎯 Overview

This platform provides a complete solution for managing a professional tutoring business, targeting NCEA and Cambridge students (Years 9-13) in Auckland, New Zealand. It includes:

- **Public Website**: Marketing pages, booking system, blog, and resources
- **Student Portal**: Session management, progress tracking, resources, gamification
- **Parent Portal**: Child monitoring, payment management, progress reports
- **Tutor Admin Panel**: Complete business management, scheduling, analytics

## ✨ Features

### Public Website
- Modern landing page with CTAs and testimonials
- Subject pages (Physics, Mathematics, English Literature, Science)
- Services and pricing information
- NCEA/Cambridge information hub
- Blog with study tips and exam preparation guides
- Online booking system with availability checking
- Trial session requests
- SEO-optimized pages

### Student Portal
- **Dashboard**: Upcoming sessions, progress overview, goals tracker
- **Session Management**: View, reschedule, rate sessions
- **Progress Tracking**: Grades, practice tests, topic mastery
- **Resource Library**: Past papers, study guides, worksheets
- **Study Tools**: Flashcards, timers, note-taking
- **Achievements & Gamification**: Badges, streaks, points
- **Messaging**: Direct communication with tutor

### Parent Portal
- Child's session schedule and attendance
- Progress reports and academic tracking
- Financial management and payment history
- Invoice viewing and payment
- Communication with tutor
- Session booking and management

### Tutor Admin Panel
- **Dashboard**: Today's schedule, pending bookings, business stats
- **Schedule Management**: Calendar, availability, recurring sessions
- **Student Management**:
  - Individual profiles with academic history
  - Progress tracking and notes
  - Custom pricing per student
  - Session history and reports
- **Financial Management**:
  - Automated invoicing with GST
  - Payment tracking
  - Revenue analytics
  - Expense tracking
  - Financial reports (daily/weekly/monthly/yearly)
- **Content Management**: Update website content, blog posts
- **Resource Management**: Upload and organize study materials
- **Analytics Dashboard**:
  - Student metrics
  - Session statistics
  - Revenue breakdown by subject/curriculum
  - Conversion tracking
- **Communication Center**:
  - Email templates
  - Automated emails
  - Message center

## 🛠 Technology Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL 16
- **Task Queue**: Celery + Redis
- **Authentication**: JWT (Simple JWT)
- **Email**: SendGrid
- **Payment**: Stripe
- **File Storage**: AWS S3 or local
- **PDF Generation**: ReportLab / WeasyPrint
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Headless UI
- **State Management**: Zustand + React Query
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Calendar**: FullCalendar
- **Routing**: React Router v6
- **PWA**: Vite PWA Plugin

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (production)
- **WSGI**: Gunicorn
- **Monitoring**: Sentry
- **CI/CD**: GitHub Actions (to be configured)

## 📁 Project Structure

```
tutoring-platform/
├── backend/                      # Django backend
│   ├── tutoring/                 # Main Django project
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py              # Main URL configuration
│   │   ├── celery.py            # Celery configuration
│   │   └── wsgi.py              # WSGI application
│   ├── accounts/                 # User management & authentication
│   │   ├── models.py            # User, StudentProfile, ParentProfile, TutorProfile
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── core/                     # Core business models
│   │   ├── models.py            # Subject, Topic, FAQ, Testimonial, SiteSettings
│   │   └── ...
│   ├── students/                 # Student-specific features
│   │   ├── models.py            # Progress, Goals, Achievements, StudyStreak
│   │   └── ...
│   ├── sessions/                 # Booking & scheduling
│   │   ├── models.py            # Session, BookingRequest, TutorAvailability
│   │   └── ...
│   ├── finances/                 # Financial management
│   │   ├── models.py            # Invoice, Payment, Package, Expense
│   │   └── ...
│   ├── resources/                # Resource library
│   │   ├── models.py            # Resource, BlogPost, StudyTool, Flashcard
│   │   └── ...
│   ├── communications/           # Messaging & emails
│   │   ├── models.py            # EmailTemplate, Message, Notification
│   │   ├── tasks.py             # Celery tasks for automated emails
│   │   └── ...
│   ├── analytics/                # Business intelligence
│   │   ├── models.py            # BusinessMetrics, StudentEngagement
│   │   ├── tasks.py             # Analytics aggregation tasks
│   │   └── ...
│   ├── requirements.txt
│   ├── Dockerfile
│   └── manage.py
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   │   ├── layouts/         # PublicLayout, StudentLayout, etc.
│   │   │   ├── auth/            # ProtectedRoute, LoginForm
│   │   │   ├── common/          # Button, Card, Modal, etc.
│   │   │   └── ...
│   │   ├── pages/               # Page components
│   │   │   ├── public/          # Landing, About, Subjects, etc.
│   │   │   ├── auth/            # Login, Register
│   │   │   ├── student/         # Student portal pages
│   │   │   ├── parent/          # Parent portal pages
│   │   │   └── tutor/           # Tutor admin pages
│   │   ├── hooks/               # Custom React hooks
│   │   ├── api/                 # API client and endpoints
│   │   ├── store/               # Zustand stores
│   │   ├── types/               # TypeScript types
│   │   ├── utils/               # Utility functions
│   │   ├── App.tsx              # Main app component
│   │   ├── main.tsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── public/                  # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── Dockerfile
├── nginx/                        # Nginx configuration
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd tutoring-platform
```

2. **Create environment file**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Run migrations and create superuser**
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

5. **Load initial data (optional)**
```bash
docker-compose exec backend python manage.py loaddata initial_data
```

6. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Django Admin: http://localhost:8000/admin
- API Documentation: http://localhost:8000/api/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up database**
```bash
# Create PostgreSQL database
createdb tutoring_db

# Copy and configure environment
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

7. **Start Celery (in separate terminals)**
```bash
# Worker
celery -A tutoring worker -l info

# Beat scheduler
celery -A tutoring beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start development server**
```bash
npm run dev
```

## ⚙️ Configuration

### Environment Variables

Key environment variables (see `backend/.env.example` for full list):

- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SENDGRID_API_KEY`: SendGrid API key for emails
- `STRIPE_SECRET_KEY`: Stripe API key for payments
- `AWS_ACCESS_KEY_ID`: AWS credentials for S3 storage
- `FRONTEND_URL`: Frontend URL for CORS

### Initial Data Setup

The platform requires some initial data to function:

1. **Subjects**: Create subjects (Physics, Mathematics, English Literature, Science)
2. **Topics**: Add topics for each subject
3. **Pricing Tiers**: Set up pricing by year level
4. **Email Templates**: Configure automated email templates
5. **Site Settings**: Configure business hours, policies, contact info

You can do this via:
- Django Admin (`/admin`)
- API endpoints
- Custom management commands (to be created)

## 📊 Database Schema

### Core Models

**User & Profiles**
- `User`: Custom user model with email authentication
- `StudentProfile`: Extended student information
- `ParentProfile`: Parent information
- `TutorProfile`: Tutor information

**Academic**
- `Subject`: Subjects offered (Physics, Maths, English, Science)
- `Topic`: Topics within each subject
- `StudentSubjectEnrollment`: Student-subject relationships
- `TopicMastery`: Student mastery of topics

**Sessions & Booking**
- `Session`: Tutoring sessions
- `BookingRequest`: Student booking requests
- `TutorAvailability`: Tutor availability schedule
- `RecurringSession`: Recurring session templates
- `Waitlist`: Waitlist for full slots

**Financial**
- `Invoice`: Invoices with GST
- `Payment`: Payment records
- `Package`: Session packages with discounts
- `StudentPackage`: Student package purchases
- `Expense`: Business expenses
- `Discount`: Discount codes
- `ReferralReward`: Referral rewards

**Resources**
- `Resource`: Study materials (past papers, worksheets, etc.)
- `BlogPost`: Blog posts and articles
- `StudyTool`: Study tools (flashcards, timers)
- `Flashcard`: Individual flashcards

**Communications**
- `EmailTemplate`: Email templates
- `EmailLog`: Email sending log
- `Message`: Internal messaging
- `Notification`: In-app notifications
- `AutomationRule`: Communication automation rules

**Analytics**
- `BusinessMetrics`: Business KPIs
- `SubjectPerformance`: Subject-level metrics
- `StudentEngagement`: Student engagement metrics

## 📡 API Documentation

### Authentication
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh token
- `POST /api/auth/register/` - Register new user

### Subjects & Topics
- `GET /api/core/subjects/` - List subjects
- `GET /api/core/subjects/{id}/` - Subject details
- `GET /api/core/topics/` - List topics

### Sessions
- `GET /api/sessions/` - List sessions
- `POST /api/sessions/` - Create session
- `GET /api/sessions/availability/` - Check availability
- `POST /api/sessions/booking-requests/` - Submit booking request

### Students
- `GET /api/students/progress/` - Student progress
- `GET /api/students/achievements/` - Student achievements
- `POST /api/students/goals/` - Create goal

### Finances
- `GET /api/finances/invoices/` - List invoices
- `POST /api/finances/payments/` - Record payment
- `GET /api/finances/packages/` - List packages

Full API documentation available at `/api/docs/` when running.

## 🚢 Deployment

### Production Checklist

1. **Environment**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Set up HTTPS with SSL certificates

2. **Database**
   - Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
   - Set up automated backups
   - Configure connection pooling

3. **Static & Media Files**
   - Configure AWS S3 or CloudFront
   - Set `USE_S3=True` in environment

4. **Email**
   - Configure SendGrid with verified domain
   - Set up email templates

5. **Payment**
   - Use production Stripe keys
   - Configure webhooks

6. **Monitoring**
   - Set up Sentry for error tracking
   - Configure uptime monitoring
   - Set up log aggregation

7. **Security**
   - Enable CSRF protection
   - Configure CORS properly
   - Set up rate limiting
   - Regular security updates

### Deployment Platforms

**Recommended:**
- **Backend**: DigitalOcean App Platform, AWS ECS, or Railway
- **Database**: DigitalOcean Managed PostgreSQL or AWS RDS
- **Redis**: DigitalOcean Managed Redis or AWS ElastiCache
- **Frontend**: Vercel, Netlify, or CloudFlare Pages
- **Storage**: AWS S3

## 💼 Business Features

### Automated Workflows

**Email Automations:**
- Booking confirmation (immediate)
- Session reminders (24hr, 1hr before)
- Invoice generation (after session)
- Payment reminders (3 days, 7 days overdue)
- Monthly progress reports
- Exam preparation reminders
- Package expiring notifications
- Inactive student re-engagement

**Smart Scheduling:**
- Automatic conflict detection
- Buffer time between sessions
- Recurring session management
- Waitlist notifications
- Capacity management

### Financial Management

**Invoicing:**
- Automated invoice generation
- GST calculation (15%)
- Package deal handling
- Discount application
- Multiple payment methods
- Payment tracking
- Overdue management

**Reporting:**
- Revenue by period (daily/weekly/monthly/yearly)
- Revenue by subject and curriculum
- Outstanding payments
- Expense tracking
- Profit margins
- Tax summaries for GST returns

### Student Engagement

**Progress Tracking:**
- Grade progression
- Topic mastery levels
- Practice test results
- Session attendance
- Homework completion

**Gamification:**
- Achievement badges
- Study streaks
- Points system
- Leaderboards (optional)
- Milestone celebrations

### Parent Features

**Monitoring:**
- Real-time session updates
- Progress reports
- Attendance tracking
- Grade improvements

**Financial:**
- View invoices
- Make payments
- Payment history
- Package management

## 📚 Additional Features

### Trial Sessions
- Free 30-minute trial sessions
- Automated follow-up sequence
- Conversion tracking

### Package Deals
- 5, 10, 20, 30 session packages
- Automatic discounts (3%, 5%, 10%, 15%)
- Usage tracking
- Expiration management

### Referral Program
- Unique referral codes
- Automated rewards
- Referral tracking

### Group Sessions
- Multi-student booking
- Discounted group rates
- Split invoicing

### Resource Library
- NCEA past papers with answers
- Cambridge past papers with mark schemes
- Custom worksheets
- Study guides
- Video links
- Organized by subject, curriculum, year level

## 📞 Support

For questions or issues:
- Documentation: This README
- API Docs: `/api/docs/`
- Django Admin: `/admin/`

## 📄 License

Proprietary - All rights reserved

## 🙏 Acknowledgments

Built for professional tutoring services in Auckland, New Zealand, specializing in NCEA and Cambridge curricula for secondary school students (Years 9-13).

---

**Version**: 1.0.0
**Last Updated**: 2025
**Status**: In Development
