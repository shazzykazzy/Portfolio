# ⚡ Quick Start Guide - Weight Gain RPG

Get started in under 2 minutes!

## 🚀 Super Quick Start (One Command)

```bash
./run.sh
```

That's it! The script will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Launch the app at http://localhost:5000

## 📝 Step-by-Step (First Time Users)

### 1. Make sure you have Python 3.8+
```bash
python3 --version
```

### 2. Run the app
```bash
chmod +x run.sh  # Make script executable (first time only)
./run.sh
```

### 3. Open in browser
```
http://localhost:5000
```

### 4. Initialize your character
You'll see a welcome screen. Enter:
- Your name
- Starting weight (kg)
- Target weight (default: 90kg)
- Target date (default: July 22, 2027)

Click **"BEGIN ADVENTURE!"** 🎮

### 5. Start logging!
- Click **"Log Weight"** to record your first entry
- Earn **50 XP** instantly!
- Unlock your first achievement!
- Watch the confetti! 🎉

## 🎯 Your First 5 Minutes

### Minute 1: Log Your Weight
- Click "Log Weight"
- Enter current weight
- See your first XP popup!
- Achievement unlocked: **First Step** 🎯

### Minute 2: Explore the Dashboard
- Check your RPG stats
- See your Power Level
- View the progress chart
- Check daily quests

### Minute 3: Complete a Quest
- Try logging your calories
- Or upload a progress photo
- Or write a journal entry
- Watch your XP bar fill up!

### Minute 4: Check Achievements
- Click "View All" in achievements section
- See what's available to unlock
- Plan your next achievements

### Minute 5: Set Your Routine
- Decide on your daily logging time
- Check the required weekly gain rate
- Set up your first streak goal

## 🎮 Daily Routine (2 minutes/day)

### Morning Routine (1 minute)
1. Log your weight after waking up
2. Bonus XP for logging before 8am!
3. Check today's quests

### Evening Routine (1 minute)
1. Log your calories
2. Write a quick journal entry
3. Upload a progress photo (weekly)

**That's it!** Maintain your streak and watch the XP roll in! 🔥

## 🏆 First Week Goals

Day 1:
- [ ] Initialize account
- [ ] Log first weight
- [ ] Unlock "First Step" achievement

Day 2:
- [ ] Log weight again
- [ ] Start your streak! 🔥

Day 3-6:
- [ ] Keep the streak going
- [ ] Try logging calories
- [ ] Upload first progress photo

Day 7:
- [ ] Complete 7-day streak
- [ ] Unlock "Week Warrior" achievement
- [ ] Earn 500 XP bonus! 🎉

## 💡 Pro Tips

### Maximize XP
- Log before 8am for bonus XP (+25)
- Complete all daily quests
- Maintain your streak (combo multipliers coming soon)
- Upload photos regularly (+100 XP each)
- Write journal entries (+40 XP each)

### Build Streaks Fast
- Set a daily alarm for logging
- Log at the same time each day
- Don't skip weekends!
- Use the app as your morning routine

### Unlock Achievements Faster
- Check achievement list to see what's close
- Focus on achievable ones first
- Track your progress toward milestones
- Combine activities (log weight + calories = 2 quests done)

### Level Up Quickly
- Complete all 5 daily quests = 370 XP/day
- Weekly photos = 700 XP/week
- Maintain 7-day streak = 500 XP bonus
- Hit calorie targets for extra XP

## 🎨 Customize Your Experience

### Change Theme (unlockable)
- Reach level 10 to unlock new themes
- Level 20 for more themes
- Level 30 for premium themes

### Track What Matters
- Focus on weight if that's your main metric
- Add calories if tracking nutrition
- Use photos to see visual progress
- Journal for mental clarity

## ❓ Quick FAQ

**Q: Do I need to log weight every day?**
A: Not required, but daily logging builds streaks and earns more XP!

**Q: What if I miss a day?**
A: No worries! Your streak resets, but you don't lose any XP or achievements you've earned.

**Q: Can I change my target weight?**
A: Currently set at initialization. Future update will allow changes.

**Q: How do I earn XP fastest?**
A: Complete all 5 daily quests every day (370 XP/day) and maintain your streak!

**Q: What happens when I reach level 50?**
A: You become a **Gain God** and unlock all features! But you can keep earning XP and achievements.

**Q: Can I export my data?**
A: Database is stored in `database/weight_gain_rpg.db` - you can backup this file.

**Q: Is there a mobile app?**
A: It's a web app that works great on mobile browsers! PWA version coming soon.

## 🐛 Troubleshooting

### "Port 5000 already in use"
```bash
# Find what's using it
lsof -i :5000
# Kill that process
kill -9 <PID>
# Or edit backend/app.py and change port to 5001
```

### "Module not found" error
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

### Database not creating
```bash
# Make sure directory exists
mkdir -p database
# Try running again
cd backend && python app.py
```

### Chart not showing
- Make sure you have at least 2 weight logs
- Check browser console for errors (F12)
- Try refreshing the page

## 🎓 Next Steps

Once you're comfortable with the basics:

1. **Read the full README.md** for all features
2. **Check FEATURES.md** for complete feature list
3. **Review DEPLOYMENT.md** to deploy online
4. **Join the community** and share your progress!

## 📱 Mobile Tips

### Add to Home Screen (iPhone)
1. Open in Safari
2. Tap share button
3. "Add to Home Screen"
4. Use like a native app!

### Add to Home Screen (Android)
1. Open in Chrome
2. Tap menu (3 dots)
3. "Add to Home Screen"
4. Enjoy!

## 🎉 You're Ready!

That's all you need to get started! The app is designed to be intuitive and fun.

**Remember:**
- Log daily for streaks 🔥
- Complete quests for XP ⭐
- Unlock achievements 🏆
- Level up your character 💪
- Reach 90kg by July 22, 2027! 🎯

## 🚀 Launch Command

```bash
./run.sh
```

**Now go crush those gains! 🎮💪**

---

Need help? Check the full **README.md** or open an issue!
