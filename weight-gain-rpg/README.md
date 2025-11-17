# 🎮 Weight Gain RPG - Level Up Your Gains! 💪

An **epic, highly gamified** weight gain tracking app that feels like an addictive fitness RPG game! Track your journey to 90kg by July 22, 2027 with vibrant animations, achievements, daily quests, and RPG-style progression mechanics.

![Version](https://img.shields.io/badge/version-1.0.0-purple)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

### 🎯 Core Functionality
- **Weight Logging** with date/time stamps and notes
- **Visual Progress Tracking** with animated charts and graphs
- **Countdown Timer** to target date (July 22, 2027)
- **Target System**: Reach 90kg bodyweight
- **Smart Calculations**: Required weekly/monthly gain rates
- **Progress Photos**: Upload and timeline view
- **Journal Entries**: Track your thoughts and mood

### 🎮 Epic Gamification

#### RPG-Style Progression System
- **Character Avatar** that evolves as you gain weight
- **XP System**: Earn XP for every action (logging, photos, hitting targets)
- **Level System** with epic level-up animations (50 levels!)
- **Title Progression**:
  - Level 1: Novice Gainer
  - Level 10: Determined Gainer
  - Level 20: Mass Builder
  - Level 30: Mass Master
  - Level 50: Gain God
- **Power Level**: RPG-style metric combining all your stats

#### Achievement & Badge System
- **50+ Unique Achievements** with cool icons
- **Rarity System**: Common, Rare, Epic, Legendary
- **Achievement Categories**:
  - First milestones (First Step, Picture Perfect)
  - Streak achievements (Week Warrior, Month Master, Unstoppable)
  - Weight milestones (+2kg Beast, +5kg Titan, +10kg Colossus)
  - Consistency rewards (Century Club, Year of Dedication)
  - Ultimate achievements (Goal Crusher, Gain Legend)
- **Animated Popups** with confetti celebrations
- **Badge Collection** showcase

#### Daily Quest System
- **5 Daily Quests** that refresh each day:
  - Log your weight today (+50 XP)
  - Log your calories (+30 XP)
  - Hit your calorie target (+150 XP)
  - Upload a progress photo (+100 XP)
  - Write a journal entry (+40 XP)
- **Visual Quest Tracker** with checkboxes
- **Streak Bonuses** for consecutive completions

#### RPG Stats Dashboard
Character stats displayed like an RPG game:
- **STR (Strength)**: Based on logging consistency
- **MASS**: Current weight
- **MOMENTUM**: Monthly gain rate
- **CONSISTENCY**: Current streak
- **DEDICATION**: Days since start
- **POWER LEVEL**: Combined metric of all stats

### 🎨 Visual Design

#### Vibrant Color Palette
- **Primary Gradient**: Electric purple (#7C3AED) to hot pink (#EC4899)
- **Secondary Gradient**: Cyan (#06B6D4) to blue (#3B82F6)
- **Success Colors**: Vibrant green (#10B981)
- **Warning Colors**: Orange to yellow gradients
- **Dark Mode**: Deep space backgrounds (#0F172A)
- **Neon Accents**: Glowing effects throughout

#### Animations & Effects
- **Particle.js Background**: Interactive floating particles
- **Confetti Celebrations**: On achievements and milestones
- **Smooth Transitions**: 300-500ms on all interactions
- **Hover Effects**: Scale transforms and glows
- **Progress Bars**: Gradient fills with shine effects
- **Level-Up Fanfare**: Full-screen celebration
- **Floating Animations**: Cards and avatars gently float
- **Glassmorphism**: Frosted glass card effects

### 📊 Data & Analytics
- **Interactive Weight Chart**: Beautiful gradient-filled Chart.js visualization
- **Trend Analysis**: Track your momentum and consistency
- **Streak Tracking**: Never break the chain! 🔥
- **Progress Predictions**: See when you'll hit milestones
- **Color-Coded Performance**: Green (on track), Red (behind), Gold (ahead)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
```bash
cd weight-gain-rpg
```

2. **Run the setup script**
```bash
chmod +x run.sh
./run.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create uploads directory
mkdir -p frontend/static/uploads

# Run the app
cd backend
python app.py
```

3. **Open your browser**
```
http://localhost:5000
```

4. **Initialize your character**
- Enter your name
- Set your starting weight
- Confirm target (90kg by July 22, 2027)
- Start your journey! 🎮

## 📱 Usage Guide

### Logging Weight
1. Click **"Log Weight"** button
2. Enter your current weight
3. Add optional notes
4. Earn **+50 XP** instantly!
5. Bonus **+25 XP** if logged before 8am

### Completing Quests
- Daily quests appear in the **Daily Quests** section
- Complete them to earn XP and maintain streaks
- Quests reset every day at midnight
- Completing all quests gives bonus XP multipliers

### Unlocking Achievements
- Achievements unlock automatically as you progress
- Watch for the epic popup notification
- Check the Achievements section to see progress
- Rare and Legendary achievements give massive XP

### Leveling Up
- Gain XP through logging, quests, and achievements
- Each level requires more XP (exponential curve)
- Level ups give new titles and unlock features
- Watch the epic level-up animation!

### Tracking Progress
- View your **Weight Chart** for visual trends
- Check **Required Gain Rate** to stay on track
- Monitor your **Power Level** and RPG stats
- Review **Streak Counter** to maintain momentum

## 🗄️ Database Schema

### Tables
- **user_profile**: User data, XP, level, title
- **weight_logs**: All weight entries with timestamps
- **progress_photos**: Photo uploads with metadata
- **achievements**: All available achievements
- **user_achievements**: Unlocked achievements per user
- **daily_quests**: Available quests
- **user_quest_progress**: Daily quest completion tracking
- **calorie_logs**: Calorie intake tracking
- **journal_entries**: Journal and mood entries
- **level_rewards**: XP requirements and rewards per level
- **streaks**: Streak tracking by type
- **stats_history**: Historical stats for analytics

## 🎨 Customization

### Themes
The app supports multiple color themes (unlockable through leveling):
- Default: Purple/Pink gradient
- Cyan/Blue gradient (unlock at level 10)
- Green gradient (unlock at level 20)
- Orange/Yellow gradient (unlock at level 30)
- Custom themes (unlock at level 40+)

### Avatar Customization
As you level up, unlock:
- Different avatar emojis
- Animated avatars
- Custom avatar backgrounds
- Special effects and badges

## 🔧 API Reference

### Endpoints

#### User Initialization
```http
POST /api/init
Content-Type: application/json

{
  "username": "Player",
  "start_weight": 75.5,
  "target_weight": 90.0,
  "target_date": "2027-07-22"
}
```

#### Log Weight
```http
POST /api/weight
Content-Type: application/json

{
  "user_id": 1,
  "weight": 76.2,
  "notes": "Feeling strong!"
}
```

#### Get Dashboard Data
```http
GET /api/dashboard?user_id=1
```

#### Get Achievements
```http
GET /api/achievements?user_id=1
```

#### Upload Progress Photo
```http
POST /api/photo
Content-Type: multipart/form-data

photo: [file]
user_id: 1
caption: "30 days in!"
```

#### Log Calories
```http
POST /api/calories
Content-Type: application/json

{
  "user_id": 1,
  "calories": 3500,
  "target_calories": 3200
}
```

## 📦 Project Structure

```
weight-gain-rpg/
├── backend/
│   ├── app.py              # Flask application & API endpoints
│   └── database.py         # Database schema & operations
├── frontend/
│   ├── templates/
│   │   └── index.html      # Main dashboard template
│   └── static/
│       ├── css/
│       ├── js/
│       │   └── app.js      # Frontend JavaScript logic
│       ├── images/
│       ├── sounds/
│       └── uploads/        # User uploaded photos
├── database/
│   └── weight_gain_rpg.db  # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
├── run.sh                  # Launch script
├── .gitignore
└── README.md
```

## 🌟 Advanced Features

### Streak System
- **Current Streak**: Days of consecutive logging
- **Longest Streak**: Personal best
- **Streak Multipliers**: Bonus XP for long streaks
- **Comeback Mechanic**: Special achievement for recovering a broken streak

### Power Level Calculation
```python
power_level = (level * 100) +
              (weight_gained * 50) +
              (current_streak * 10) +
              (total_xp / 10)
```

### XP Sources
- Log weight: 50 XP (75 if before 8am)
- Upload photo: 100 XP
- Log calories: 30 XP
- Hit calorie target: 80 XP
- Write journal: 40 XP
- Complete achievement: 100-10000 XP
- Level up bonus: Variable

### Rarity Tiers
- **Common** (Gray): Basic achievements, frequent unlocks
- **Rare** (Blue): Moderate challenges, weekly unlocks
- **Epic** (Purple): Difficult challenges, monthly unlocks
- **Legendary** (Gold): Ultimate achievements, rare unlocks

## 🚢 Deployment

### Local Development
```bash
./run.sh
```

### Production Deployment

#### Option 1: Traditional Server
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### Option 2: Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "backend/app.py"]
```

```bash
docker build -t weight-gain-rpg .
docker run -p 5000:5000 weight-gain-rpg
```

#### Option 3: Cloud Platforms
- **Heroku**: Add `Procfile` with `web: gunicorn backend.app:app`
- **Railway**: Connect GitHub repo, auto-deploys
- **Render**: Deploy as web service
- **PythonAnywhere**: Upload files, configure WSGI

## 🎯 Roadmap

### v1.1 - Social Features
- [ ] Share achievements on social media
- [ ] Export achievement cards as images
- [ ] Comparison with past self leaderboard

### v1.2 - Integration
- [ ] MyFitnessPal calorie import
- [ ] Garmin Connect weight sync
- [ ] Apple Health integration
- [ ] Google Fit integration

### v1.3 - Enhanced Gamification
- [ ] Weekly challenges with mega rewards
- [ ] Boss battles (monthly weight targets)
- [ ] Seasonal events
- [ ] Lucky week events (double XP)
- [ ] Achievement hunting mode

### v1.4 - PWA & Mobile
- [ ] Progressive Web App capabilities
- [ ] Install as mobile app
- [ ] Push notifications
- [ ] Offline mode
- [ ] Home screen widgets

### v2.0 - AI & Predictions
- [ ] ML-powered weight predictions
- [ ] Personalized recommendations
- [ ] Smart calorie targets
- [ ] Achievement difficulty tuning

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database (WARNING: Deletes all data!)
rm database/weight_gain_rpg.db
python backend/app.py  # Will recreate
```

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Dependencies Not Installing
```bash
# Upgrade pip
pip install --upgrade pip

# Try with --user flag
pip install --user -r requirements.txt
```

## 📄 License

MIT License - Feel free to use and modify!

## 🙏 Credits

### Libraries & Frameworks
- **Flask**: Web framework
- **Chart.js**: Beautiful charts
- **Tailwind CSS**: Utility-first CSS
- **Particles.js**: Interactive backgrounds
- **Canvas Confetti**: Celebration effects
- **SQLite**: Database

### Inspiration
Built with ❤️ for anyone on a weight gain journey who wants to make tracking fun and engaging!

## 📞 Support

Having issues? Want to contribute?

- Open an issue on GitHub
- Submit a pull request
- Share your progress and achievements!

---

**Made with 💜 and 💪 - Let's reach those gains together! 🎮**

⚡ **Start your journey today and become a Gain Legend!** ⚡
