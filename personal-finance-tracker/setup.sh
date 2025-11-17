#!/bin/bash

# WealthTrack Setup Script

echo "🚀 Setting up WealthTrack Personal Finance Tracker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

# Build and start containers
echo "🏗️  Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec -T backend python manage.py migrate

# Create default categories
echo "📁 Creating default categories..."
docker-compose exec -T backend python manage.py shell << EOF
from transactions.models import Category

# Income categories
income_cats = [
    ('Salary/Wages', 'income'),
    ('Tutoring Income', 'income'),
    ('Investment Income', 'income'),
    ('Side Hustle', 'income'),
    ('Gifts Received', 'income'),
    ('Other Income', 'income'),
]

# Expense categories
expense_cats = [
    ('Housing', 'expense'),
    ('Transportation', 'expense'),
    ('Food & Dining', 'expense'),
    ('Personal', 'expense'),
    ('Entertainment', 'expense'),
    ('Financial', 'expense'),
    ('Education', 'expense'),
    ('Gifts & Donations', 'expense'),
    ('Miscellaneous', 'expense'),
]

for name, cat_type in income_cats + expense_cats:
    Category.objects.get_or_create(name=name, category_type=cat_type, user=None)

print("✅ Default categories created")
EOF

# Create superuser
echo ""
echo "👤 Create admin user:"
docker-compose exec backend python manage.py createsuperuser

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   Admin:     http://localhost:8000/admin"
echo "   API Docs:  http://localhost:8000/api/docs"
echo ""
echo "🛠️  Useful commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Run migrations:   docker-compose exec backend python manage.py migrate"
echo "   Create superuser: docker-compose exec backend python manage.py createsuperuser"
echo ""
echo "💡 Next steps:"
echo "   1. Log in to http://localhost:3000"
echo "   2. Set up your accounts"
echo "   3. Add some transactions"
echo "   4. Create your first budget"
echo ""
echo "Happy tracking! 💰📊✨"
