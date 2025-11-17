# 💰 WealthTrack - Personal Finance Tracker

A comprehensive personal finance tracking and forecasting application built for New Zealand users, inspired by PocketSmith. Track your net worth, manage budgets, monitor investments, and forecast your financial future.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.3-blue.svg)

## ✨ Features

### 📊 Dashboard & Overview
- **Net Worth Widget**: Track your total net worth with historical trends and projections
- **Cash Flow Summary**: Monitor income vs expenses with real-time insights
- **Quick Stats**: Instant view of liquid cash, investments, and debt
- **Upcoming Bills**: Never miss a payment with smart reminders
- **Insights Feed**: AI-powered financial insights and recommendations

### 💳 Account Management
- **Multiple Account Types**: Bank accounts, savings, credit cards, investments, assets, and liabilities
- **Balance Tracking**: Historical balance tracking for all accounts
- **Multi-Currency Support**: Primary currency NZD with support for USD, AUD, GBP, EUR
- **Account Groups**: Organize accounts (e.g., "Emergency Fund" spanning multiple accounts)
- **Auto-Sync Ready**: Built for future bank API integration

### 📝 Transaction Management
- **Smart Categorization**: Automatic transaction categorization with learning
- **Split Transactions**: Divide transactions across multiple categories
- **Recurring Transactions**: Set up and auto-create recurring income/expenses
- **Receipt Attachments**: Upload and store receipts with transactions
- **Tags & Search**: Powerful filtering and search capabilities
- **Bulk Operations**: Import from CSV, bulk edit, and categorize

### 💰 Budgeting System
- **Flexible Budgets**: Weekly, monthly, quarterly, or annual budgets
- **Multiple Budget Types**: Standard, percentage-based, zero-based, envelope
- **Budget Tracking**: Real-time progress tracking with pace indicators
- **Rollover Support**: Carry unused budget to next period
- **Budget Templates**: Save and reuse budget configurations
- **Performance Analytics**: Detailed budget vs actual analysis

### 📈 Investment Tracking
- **Portfolio Management**: Track stocks, ETFs, mutual funds, bonds, and crypto
- **Holdings**: Monitor shares, cost basis, and current value
- **Performance Tracking**: Calculate gains/losses and returns
- **Dividend Tracking**: Track dividend payments and yields
- **Asset Allocation**: Set targets and get rebalancing recommendations
- **Tax Reporting**: Capital gains and dividend summaries for NZ tax

### 🎯 Goals & Milestones
- **Financial Goals**: Set savings, debt payoff, and net worth goals
- **Progress Tracking**: Visual progress bars and projections
- **Goal Insights**: Calculate required monthly savings to hit targets
- **Milestone Celebrations**: Automatic achievements for major financial milestones
- **Goal Linking**: Auto-track goals from linked accounts

### 🔮 Forecasting & Scenarios
- **Cash Flow Forecast**: Project future account balances up to 5 years
- **Net Worth Forecast**: Predict future net worth with confidence bands
- **Scenario Planning**: Create "what-if" scenarios (buy house, job loss, etc.)
- **Goal-Based Forecasting**: Calculate when you'll reach financial goals
- **Investment Projections**: Model compound growth and retirement savings
- **Debt Payoff Planner**: Snowball vs avalanche comparison

### 📊 Reports & Analytics
- **Income vs Expenses**: Track and compare over time
- **Spending by Category**: Detailed breakdowns with drill-down
- **Cash Flow Reports**: Sankey diagrams and waterfall charts
- **Net Worth History**: Track growth over time
- **Merchant Analysis**: Identify top spending locations
- **Tax Reports**: Deductible expenses and investment income
- **Custom Reports**: Build and save custom report views
- **Scheduled Reports**: Email reports automatically

### 💡 Smart Insights
- **Spending Insights**: Unusual charges and trend detection
- **Budget Alerts**: Overspending warnings with days remaining
- **Savings Insights**: Track savings rate and compare to goals
- **Investment Insights**: Portfolio performance and rebalancing suggestions
- **Behavioral Insights**: Identify spending patterns and habits
- **Optimization Suggestions**: Actionable recommendations to improve finances

### 📅 Calendar & Reminders
- **Financial Calendar**: View all transactions, bills, and milestones
- **Bill Reminders**: Customizable reminders before due dates
- **Subscription Tracking**: Track and manage recurring subscriptions
- **Event Planning**: Budget for holidays, birthdays, and major purchases

### 🔒 Security & Privacy
- **JWT Authentication**: Secure token-based authentication
- **Data Encryption**: Sensitive data encrypted at rest
- **2FA Support**: Two-factor authentication available
- **Privacy First**: Your data stays with you
- **Audit Logging**: Track all account access and changes

### 📱 Mobile Experience
- **Progressive Web App**: Install on mobile home screen
- **Touch Optimized**: Swipe gestures and thumb-friendly design
- **Offline Support**: Work offline, sync when connected
- **Push Notifications**: Bill reminders and budget alerts
- **Quick Entry**: Add transactions in 3 taps or less

## 🏗️ Architecture

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Task Queue**: Celery + Celery Beat (scheduled tasks)
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: DRF Spectacular (OpenAPI/Swagger)

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Charts**: Recharts + Chart.js
- **Animations**: Framer Motion
- **Forms**: React Hook Form

### Database Schema
```
Users
├── UserSettings
├── NetWorthSnapshots
└── Insights

Accounts
├── BalanceHistory
└── AccountGroups

Transactions
├── Categories
├── Tags
├── RecurringTransactions
├── Bills
└── TransactionRules

Budgets
├── BudgetItems
├── BudgetTemplates
└── BudgetTemplateItems

Investments
├── InvestmentHoldings
├── InvestmentTransactions
├── Dividends
├── PortfolioSnapshots
└── AssetAllocations

Goals
├── GoalContributions
└── Milestones

Forecasting
├── Forecasts
├── ForecastDataPoints
├── Scenarios
├── ScenarioEvents
└── CashFlowProjections

Reports
├── SavedReports
├── ScheduledReports
├── SpendingPatterns
└── FinancialHealthScores
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd personal-finance-tracker
```

2. **Set up environment variables**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Run migrations**
```bash
docker-compose exec backend python manage.py migrate
```

5. **Create superuser**
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs

### Manual Setup (Development)

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

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create default categories (optional)**
```bash
python manage.py create_default_categories
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Run Celery worker (separate terminal)**
```bash
celery -A core worker -l info
```

9. **Run Celery Beat (separate terminal)**
```bash
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Run development server**
```bash
npm run dev
```

3. **Build for production**
```bash
npm run build
```

## 📖 API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/token/` - Get JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `GET /api/auth/settings/` - Get user settings
- `PUT /api/auth/settings/` - Update user settings
- `GET /api/auth/dashboard/` - Get dashboard data

### Account Endpoints
- `GET /api/accounts/` - List all accounts
- `POST /api/accounts/` - Create account
- `GET /api/accounts/{id}/` - Get account details
- `PUT /api/accounts/{id}/` - Update account
- `DELETE /api/accounts/{id}/` - Delete account
- `GET /api/accounts/summary/` - Get account summary
- `GET /api/accounts/{id}/balance_history/` - Get balance history

### Transaction Endpoints
- `GET /api/transactions/` - List transactions (with filters)
- `POST /api/transactions/` - Create transaction
- `GET /api/transactions/{id}/` - Get transaction details
- `PUT /api/transactions/{id}/` - Update transaction
- `DELETE /api/transactions/{id}/` - Delete transaction
- `POST /api/transactions/bulk_import/` - Bulk import from CSV

### Budget Endpoints
- `GET /api/budgets/` - List budgets
- `POST /api/budgets/` - Create budget
- `GET /api/budgets/{id}/` - Get budget details
- `GET /api/budgets/current/` - Get current period budget
- `GET /api/budgets/{id}/performance/` - Get budget performance

Full API documentation available at `/api/docs/` when running the server.

## 🎨 User Context (NZ-Focused)

This application is optimized for New Zealand users:

- **Default Currency**: NZD
- **Date Format**: DD/MM/YYYY
- **Timezone**: Pacific/Auckland
- **Tax Support**: FIF calculations, capital gains, dividend income
- **NZ Banks Ready**: Architecture prepared for NZ bank API integration
- **KiwiSaver**: Retirement account tracking
- **NZ Business**: Tutoring income and sole trader expense tracking

## 📊 Key Metrics Tracked

1. **Net Worth**: Total assets - total liabilities
2. **Savings Rate**: (Income - Expenses) / Income
3. **Debt-to-Income Ratio**: Total debt / Annual income
4. **Emergency Fund Coverage**: Months of expenses covered
5. **Budget Adherence Score**: % of budgets stayed within
6. **Investment Returns**: Time-weighted and money-weighted
7. **Financial Health Score**: Overall score (0-100)

## 🔄 Scheduled Tasks

The following tasks run automatically via Celery Beat:

- **Daily 00:05**: Create net worth snapshots
- **Daily 00:10**: Create account balance snapshots
- **Every 4 hours**: Update investment prices (when API configured)
- **Daily 01:00**: Recalculate forecasts
- **Daily 02:00**: Process recurring transactions
- **Daily 06:00**: Generate daily insights
- **Daily 09:00**: Send bill reminders

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## 📦 Deployment

### Production Checklist

1. **Environment Variables**
   - Set `DEBUG=False`
   - Generate strong `SECRET_KEY`
   - Configure production database
   - Set up email service (SendGrid/AWS SES)
   - Configure Redis
   - Set `ALLOWED_HOSTS`
   - Configure `CORS_ALLOWED_ORIGINS`

2. **Database**
   - Run migrations
   - Create backups
   - Set up automated backups

3. **Static Files**
   - Run `python manage.py collectstatic`
   - Configure CDN (optional)

4. **Security**
   - Enable HTTPS
   - Configure firewall
   - Set up monitoring (Sentry)
   - Enable 2FA for admin users

5. **Services**
   - Start Celery workers
   - Start Celery Beat
   - Configure process manager (systemd/supervisor)

### Deployment Options

- **DigitalOcean App Platform**: Easy deployment with managed services
- **AWS**: Elastic Beanstalk or ECS
- **Railway**: Simple deployment with built-in PostgreSQL
- **Heroku**: With PostgreSQL and Redis add-ons
- **VPS**: DigitalOcean Droplet with manual setup

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by [PocketSmith](https://www.pocketsmith.com/)
- Design inspiration from [YNAB](https://www.ynab.com/) and [Mint](https://mint.intuit.com/)
- Built for NZ users with love 🇳🇿

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🗺️ Roadmap

### Phase 1 (MVP) ✅
- ✅ Core account management
- ✅ Transaction tracking
- ✅ Basic budgeting
- ✅ Net worth tracking
- ✅ Dashboard

### Phase 2 (Current)
- 🔄 Advanced budgeting
- 🔄 Goals and milestones
- 🔄 Investment tracking
- 🔄 Forecasting
- 🔄 Smart insights

### Phase 3 (Future)
- ⏳ Bank API integrations (NZ banks)
- ⏳ Sharesight integration
- ⏳ Mobile native apps
- ⏳ Shared finances (multi-user)
- ⏳ Advanced AI insights
- ⏳ Receipt OCR
- ⏳ Voice transactions

## 🏆 Goals

**Mission**: Help users understand their money, make better decisions, and achieve financial freedom through clarity, insight, and automation.

**Vision**: Become the #1 personal finance app for New Zealand users, rivaling international products while being tailored for Kiwi needs.

---

**Built with ❤️ for financial independence** 💪📊✨
