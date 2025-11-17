# 👨‍💻 Development Guide

## Project Overview

This is a comprehensive full-stack tutoring platform with:
- **Django REST Framework** backend with PostgreSQL
- **React + TypeScript** frontend with Tailwind CSS
- **Celery** for background tasks
- **Redis** for caching and message broker
- **Docker** for containerization

## Architecture

### Backend Architecture

```
backend/
├── tutoring/           # Main Django project
│   ├── settings.py    # Configuration
│   ├── urls.py        # Main URL routing
│   └── celery.py      # Celery configuration
│
├── accounts/          # Authentication & users
├── core/              # Core business logic
├── students/          # Student features
├── sessions/          # Booking & scheduling
├── finances/          # Payments & invoicing
├── resources/         # Resource library
├── communications/    # Messaging & emails
└── analytics/         # Reporting & analytics
```

### Frontend Architecture

```
frontend/src/
├── components/        # Reusable components
│   ├── layouts/      # Layout components
│   ├── auth/         # Auth components
│   └── common/       # Shared components
│
├── pages/            # Page components
│   ├── public/      # Public website
│   ├── student/     # Student portal
│   ├── parent/      # Parent portal
│   └── tutor/       # Tutor admin
│
├── hooks/           # Custom React hooks
├── api/             # API client
├── store/           # State management
├── types/           # TypeScript types
└── utils/           # Utilities
```

## Development Workflow

### Creating a New Feature

#### 1. Backend (Django)

**a. Create/Update Models**

```python
# Example: students/models.py
class StudentGoal(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_date = models.DateField()
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**b. Create Migration**

```bash
python manage.py makemigrations
python manage.py migrate
```

**c. Create Serializer**

```python
# students/serializers.py
from rest_framework import serializers
from .models import StudentGoal

class StudentGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGoal
        fields = '__all__'
```

**d. Create View**

```python
# students/views.py
from rest_framework import viewsets
from .models import StudentGoal
from .serializers import StudentGoalSerializer

class StudentGoalViewSet(viewsets.ModelViewSet):
    queryset = StudentGoal.objects.all()
    serializer_class = StudentGoalSerializer

    def get_queryset(self):
        # Filter by current user
        return StudentGoal.objects.filter(
            student__user=self.request.user
        )
```

**e. Add URLs**

```python
# students/urls.py
from rest_framework.routers import DefaultRouter
from .views import StudentGoalViewSet

router = DefaultRouter()
router.register(r'goals', StudentGoalViewSet)

urlpatterns = router.urls
```

#### 2. Frontend (React + TypeScript)

**a. Define Types**

```typescript
// src/types/student.ts
export interface StudentGoal {
  id: number
  student: number
  title: string
  description: string
  target_date: string
  is_achieved: boolean
  created_at: string
}
```

**b. Create API Client**

```typescript
// src/api/students.ts
import axios from 'axios'
import { StudentGoal } from '@/types/student'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const studentAPI = {
  getGoals: () =>
    axios.get<StudentGoal[]>(`${API_URL}/api/students/goals/`),

  createGoal: (data: Partial<StudentGoal>) =>
    axios.post<StudentGoal>(`${API_URL}/api/students/goals/`, data),

  updateGoal: (id: number, data: Partial<StudentGoal>) =>
    axios.patch<StudentGoal>(`${API_URL}/api/students/goals/${id}/`, data),

  deleteGoal: (id: number) =>
    axios.delete(`${API_URL}/api/students/goals/${id}/`),
}
```

**c. Create Component**

```typescript
// src/components/student/GoalsList.tsx
import { useQuery } from '@tanstack/react-query'
import { studentAPI } from '@/api/students'

export default function GoalsList() {
  const { data: goals, isLoading } = useQuery({
    queryKey: ['student-goals'],
    queryFn: () => studentAPI.getGoals().then(res => res.data),
  })

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      <h2>My Goals</h2>
      {goals?.map(goal => (
        <div key={goal.id}>
          <h3>{goal.title}</h3>
          <p>{goal.description}</p>
        </div>
      ))}
    </div>
  )
}
```

### Adding Celery Tasks

**1. Create Task**

```python
# communications/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_session_reminder(session_id):
    from sessions.models import Session
    session = Session.objects.get(id=session_id)

    send_mail(
        subject=f'Session Reminder: {session.subject.name}',
        message=f'You have a session tomorrow at {session.scheduled_start_time}',
        from_email='noreply@tutoring.com',
        recipient_list=[session.student.user.email],
    )
```

**2. Schedule Task**

```python
# In celery.py beat_schedule
app.conf.beat_schedule = {
    'send-session-reminders': {
        'task': 'communications.tasks.send_session_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

### Testing

#### Backend Tests

```python
# students/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User, StudentProfile

class StudentGoalTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='student@test.com',
            password='password123',
            role='STUDENT'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_goal(self):
        response = self.client.post('/api/students/goals/', {
            'title': 'Achieve Excellence',
            'description': 'Get Excellence in Physics',
            'target_date': '2024-12-31'
        })
        self.assertEqual(response.status_code, 201)
```

Run tests:
```bash
pytest
# or
python manage.py test
```

#### Frontend Tests

```typescript
// src/components/__tests__/GoalsList.test.tsx
import { render, screen } from '@testing-library/react'
import GoalsList from '../student/GoalsList'

test('renders goals list', () => {
  render(<GoalsList />)
  expect(screen.getByText('My Goals')).toBeInTheDocument()
})
```

## Common Development Tasks

### Database Operations

**Reset Database**
```bash
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

**Create Migration**
```bash
python manage.py makemigrations app_name
python manage.py sqlmigrate app_name 0001  # View SQL
python manage.py migrate
```

**Shell Access**
```bash
python manage.py shell
>>> from accounts.models import User
>>> User.objects.all()
```

### API Development

**Test Endpoints**
```bash
# Using httpie
http GET http://localhost:8000/api/students/goals/ "Authorization: Bearer <token>"

# Using curl
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/students/goals/
```

**View API Schema**
```bash
# Access Swagger UI
http://localhost:8000/api/docs/

# Download OpenAPI schema
http://localhost:8000/api/schema/
```

### Frontend Development

**Component Development**
```bash
# Start dev server with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

**Build for Production**
```bash
npm run build
npm run preview  # Preview production build
```

## Code Style & Best Practices

### Backend (Python/Django)

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions/classes
- Keep views simple, move logic to services
- Use Django ORM efficiently (select_related, prefetch_related)

Example:
```python
from typing import List
from django.db.models import Prefetch

class StudentService:
    """Service for student-related operations"""

    @staticmethod
    def get_students_with_sessions(year_level: int) -> List[StudentProfile]:
        """Get students with their recent sessions"""
        return StudentProfile.objects.filter(
            year_level=year_level
        ).select_related(
            'user', 'parent'
        ).prefetch_related(
            Prefetch(
                'sessions',
                queryset=Session.objects.order_by('-scheduled_date')[:5]
            )
        )
```

### Frontend (TypeScript/React)

- Use functional components with hooks
- Type everything with TypeScript
- Use React Query for data fetching
- Keep components small and focused
- Extract custom hooks for reusable logic

Example:
```typescript
// Custom hook
function useStudentGoals() {
  return useQuery({
    queryKey: ['student-goals'],
    queryFn: () => studentAPI.getGoals().then(res => res.data),
  })
}

// Component
export default function GoalsList() {
  const { data: goals, isLoading, error } = useStudentGoals()

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="space-y-4">
      {goals?.map(goal => (
        <GoalCard key={goal.id} goal={goal} />
      ))}
    </div>
  )
}
```

## Environment Variables

### Backend (.env)

Required:
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SENDGRID_API_KEY` - Email service
- `STRIPE_SECRET_KEY` - Payment processing

Optional:
- `AWS_ACCESS_KEY_ID` - For S3 storage
- `SENTRY_DSN` - Error tracking
- `TWILIO_ACCOUNT_SID` - SMS (optional)

### Frontend

Create `.env.local`:
```
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLIC_KEY=pk_test_...
```

## Performance Optimization

### Backend

1. **Database Queries**
   - Use select_related() for foreign keys
   - Use prefetch_related() for reverse relations
   - Add database indexes
   - Use pagination

2. **Caching**
   ```python
   from django.core.cache import cache

   def get_subjects():
       subjects = cache.get('all_subjects')
       if not subjects:
           subjects = list(Subject.objects.all())
           cache.set('all_subjects', subjects, 3600)
       return subjects
   ```

3. **Background Tasks**
   - Move slow operations to Celery
   - Send emails asynchronously
   - Generate reports in background

### Frontend

1. **Code Splitting**
   ```typescript
   const TutorDashboard = lazy(() => import('@/pages/tutor/Dashboard'))
   ```

2. **Optimize Images**
   - Use appropriate formats (WebP)
   - Lazy load images
   - Use CDN

3. **React Query Optimization**
   ```typescript
   useQuery({
     queryKey: ['students'],
     queryFn: fetchStudents,
     staleTime: 5 * 60 * 1000,  // 5 minutes
     cacheTime: 10 * 60 * 1000,  // 10 minutes
   })
   ```

## Debugging

### Backend

**Django Debug Toolbar**
```python
# Add to INSTALLED_APPS
'debug_toolbar',

# Add to MIDDLEWARE
'debug_toolbar.middleware.DebugToolbarMiddleware',
```

**Logging**
```python
import logging
logger = logging.getLogger(__name__)

logger.info('User logged in', extra={'user_id': user.id})
logger.error('Failed to send email', exc_info=True)
```

### Frontend

**React DevTools**
- Install React DevTools browser extension
- Inspect component hierarchy
- Check props and state

**Network Debugging**
```typescript
// Add request interceptor
axios.interceptors.request.use(config => {
  console.log('API Request:', config)
  return config
})

axios.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data)
    return Promise.reject(error)
  }
)
```

## Deployment Checklist

- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use production database
- [ ] Set up static file serving (WhiteNoise or CDN)
- [ ] Configure email service
- [ ] Set up error tracking (Sentry)
- [ ] Enable HTTPS
- [ ] Set secure cookie settings
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Configure environment variables
- [ ] Test payment integration
- [ ] Set up monitoring
- [ ] Load test the application

## Useful Commands

### Django
```bash
python manage.py runserver           # Start dev server
python manage.py shell              # Django shell
python manage.py dbshell            # Database shell
python manage.py showmigrations     # Show migrations
python manage.py collectstatic      # Collect static files
python manage.py createsuperuser    # Create admin user
```

### Docker
```bash
docker-compose up -d                # Start all services
docker-compose down                 # Stop all services
docker-compose logs -f backend      # View logs
docker-compose exec backend bash    # Shell into container
docker-compose restart celery       # Restart service
```

### Git
```bash
git status
git add .
git commit -m "feat: add student goals feature"
git push origin feature-branch
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Celery Documentation](https://docs.celeryproject.org/)

---

Happy coding! 🚀
