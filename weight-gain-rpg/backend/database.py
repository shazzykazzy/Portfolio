"""
Weight Gain RPG - Database Schema and Models
Gamified weight tracking with RPG progression mechanics
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class Database:
    def __init__(self, db_path='database/weight_gain_rpg.db'):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # User Profile Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                target_weight REAL NOT NULL DEFAULT 90.0,
                target_date TEXT NOT NULL DEFAULT '2027-07-22',
                start_weight REAL,
                start_date TEXT,
                current_weight REAL,
                avatar_level INTEGER DEFAULT 1,
                total_xp INTEGER DEFAULT 0,
                current_level INTEGER DEFAULT 1,
                title TEXT DEFAULT 'Novice Gainer',
                theme TEXT DEFAULT 'purple_pink',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Weight Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weight REAL NOT NULL,
                log_date TEXT NOT NULL,
                log_time TEXT NOT NULL,
                notes TEXT,
                xp_earned INTEGER DEFAULT 50,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id)
            )
        ''')

        # Progress Photos Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                weight_at_photo REAL,
                upload_date TEXT NOT NULL,
                caption TEXT,
                xp_earned INTEGER DEFAULT 100,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id)
            )
        ''')

        # Achievements Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                achievement_key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                rarity TEXT NOT NULL CHECK(rarity IN ('common', 'rare', 'epic', 'legendary')),
                xp_reward INTEGER NOT NULL,
                requirement_type TEXT NOT NULL,
                requirement_value INTEGER NOT NULL
            )
        ''')

        # User Achievements (Unlocked)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                seen BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES user_profile(id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(id),
                UNIQUE(user_id, achievement_id)
            )
        ''')

        # Daily Quests Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                quest_type TEXT NOT NULL,
                xp_reward INTEGER NOT NULL,
                icon TEXT NOT NULL,
                requirement_count INTEGER DEFAULT 1
            )
        ''')

        # User Quest Progress
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quest_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quest_id INTEGER NOT NULL,
                progress INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                quest_date TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profile(id),
                FOREIGN KEY (quest_id) REFERENCES daily_quests(id),
                UNIQUE(user_id, quest_id, quest_date)
            )
        ''')

        # Calorie Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calorie_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                log_date TEXT NOT NULL,
                calories INTEGER NOT NULL,
                target_calories INTEGER,
                xp_earned INTEGER DEFAULT 30,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id)
            )
        ''')

        # Journal Entries Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                entry_date TEXT NOT NULL,
                entry_text TEXT NOT NULL,
                mood TEXT,
                xp_earned INTEGER DEFAULT 40,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id)
            )
        ''')

        # Level Rewards Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS level_rewards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER UNIQUE NOT NULL,
                xp_required INTEGER NOT NULL,
                title TEXT NOT NULL,
                reward_type TEXT NOT NULL,
                reward_value TEXT NOT NULL
            )
        ''')

        # Streaks Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                streak_type TEXT NOT NULL,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_activity_date TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profile(id),
                UNIQUE(user_id, streak_type)
            )
        ''')

        # Stats History (for power level calculations)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stat_date TEXT NOT NULL,
                power_level INTEGER,
                strength_stat INTEGER,
                mass_stat REAL,
                momentum_stat REAL,
                consistency_stat INTEGER,
                dedication_stat INTEGER,
                FOREIGN KEY (user_id) REFERENCES user_profile(id)
            )
        ''')

        conn.commit()
        conn.close()

        # Initialize default data
        self.init_default_data()

    def init_default_data(self):
        """Initialize achievements, quests, and level rewards"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM achievements')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return

        # Initialize Achievements
        achievements = [
            # Common Achievements
            ('first_step', 'First Step', 'Log your very first weight entry', '🎯', 'common', 100, 'weight_logs', 1),
            ('early_bird', 'Early Bird', 'Log weight before 8am', '🌅', 'common', 50, 'early_log', 1),
            ('consistent_10', 'Getting Started', 'Log weight 10 times', '📊', 'common', 200, 'weight_logs', 10),
            ('photo_first', 'Picture Perfect', 'Upload your first progress photo', '📸', 'common', 150, 'photos', 1),
            ('journal_first', 'Dear Diary', 'Write your first journal entry', '📝', 'common', 100, 'journals', 1),
            ('calorie_track', 'Calorie Counter', 'Log calories for the first time', '🍽️', 'common', 80, 'calories', 1),

            # Rare Achievements
            ('week_warrior', 'Week Warrior', 'Maintain a 7-day logging streak', '🔥', 'rare', 500, 'streak_days', 7),
            ('kg_gained_2', '+2kg Beast', 'Gain 2kg from starting weight', '💪', 'rare', 400, 'weight_gained', 2),
            ('kg_gained_5', '+5kg Titan', 'Gain 5kg from starting weight', '🏆', 'rare', 800, 'weight_gained', 5),
            ('photo_collector', 'Photo Collector', 'Upload 10 progress photos', '📷', 'rare', 600, 'photos', 10),
            ('consistent_50', 'Dedicated Logger', 'Log weight 50 times', '📈', 'rare', 1000, 'weight_logs', 50),
            ('level_10', 'Power Up!', 'Reach level 10', '⭐', 'rare', 500, 'level', 10),
            ('early_bird_10', 'Morning Champion', 'Log before 8am 10 times', '☀️', 'rare', 400, 'early_log', 10),

            # Epic Achievements
            ('month_master', 'Month Master', 'Maintain a 30-day logging streak', '🔥🔥', 'epic', 1500, 'streak_days', 30),
            ('kg_gained_10', '+10kg Colossus', 'Gain 10kg from starting weight', '💎', 'epic', 2000, 'weight_gained', 10),
            ('halfway_hero', 'Halfway Hero', 'Reach 50% of your goal', '🎖️', 'epic', 2500, 'progress_percent', 50),
            ('consistent_100', 'Century Club', 'Log weight 100 times', '💯', 'epic', 2000, 'weight_logs', 100),
            ('level_25', 'Elite Gainer', 'Reach level 25', '⭐⭐', 'epic', 1500, 'level', 25),
            ('beast_mode', 'Beast Mode', 'Gain 2kg in one month', '🦍', 'epic', 1800, 'monthly_gain', 2),
            ('photo_master', 'Photo Master', 'Upload 25 progress photos', '🎨', 'epic', 1500, 'photos', 25),
            ('calorie_champion', 'Calorie Champion', 'Hit calorie target 30 days straight', '👑', 'epic', 2000, 'calorie_streak', 30),

            # Legendary Achievements
            ('unstoppable', 'Unstoppable Force', 'Maintain a 100-day logging streak', '🔥🔥🔥', 'legendary', 5000, 'streak_days', 100),
            ('kg_gained_15', '+15kg Juggernaut', 'Gain 15kg from starting weight', '💎💎', 'legendary', 4000, 'weight_gained', 15),
            ('kg_gained_20', '+20kg Legend', 'Gain 20kg from starting weight', '👑', 'legendary', 6000, 'weight_gained', 20),
            ('goal_reached', 'Goal Crusher', 'Reach your target weight of 90kg', '🏆👑', 'legendary', 10000, 'goal_complete', 1),
            ('level_50', 'Gain Legend', 'Reach level 50', '⭐⭐⭐', 'legendary', 5000, 'level', 50),
            ('consistent_365', 'Year of Dedication', 'Log weight 365 times', '🎆', 'legendary', 8000, 'weight_logs', 365),
            ('perfect_month', 'Perfect Month', 'Complete all daily quests for 30 days', '🌟', 'legendary', 5000, 'perfect_days', 30),
        ]

        cursor.executemany('''
            INSERT INTO achievements
            (achievement_key, name, description, icon, rarity, xp_reward, requirement_type, requirement_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', achievements)

        # Initialize Daily Quests
        quests = [
            ('log_weight', 'Daily Weigh-In', 'Log your weight today', 'weight_log', 50, '⚖️', 1),
            ('log_calories', 'Calorie Tracker', 'Log your calories today', 'calorie_log', 30, '🍔', 1),
            ('hit_calorie_target', 'Surplus Master', 'Hit your calorie target', 'calorie_target', 150, '🎯', 1),
            ('upload_photo', 'Snapshot', 'Upload a progress photo', 'photo_upload', 100, '📸', 1),
            ('write_journal', 'Journal Entry', 'Write a journal entry', 'journal_entry', 40, '📖', 1),
        ]

        cursor.executemany('''
            INSERT INTO daily_quests
            (quest_key, name, description, quest_type, xp_reward, icon, requirement_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', quests)

        # Initialize Level Rewards
        level_rewards = []
        titles = [
            (1, 'Novice Gainer'),
            (5, 'Aspiring Bulker'),
            (10, 'Determined Gainer'),
            (15, 'Bulk Warrior'),
            (20, 'Mass Builder'),
            (25, 'Strength Seeker'),
            (30, 'Mass Master'),
            (35, 'Bulk Champion'),
            (40, 'Gain Expert'),
            (45, 'Mass Legend'),
            (50, 'Gain God'),
        ]

        for level in range(1, 51):
            xp_required = int(100 * (level ** 1.5))
            title = next((t[1] for t in titles if t[0] == level), f'Level {level} Gainer')
            reward_type = 'theme' if level % 10 == 0 else 'xp_boost'
            reward_value = f'theme_{level}' if level % 10 == 0 else '1.1'

            level_rewards.append((level, xp_required, title, reward_type, reward_value))

        cursor.executemany('''
            INSERT INTO level_rewards
            (level, xp_required, title, reward_type, reward_value)
            VALUES (?, ?, ?, ?, ?)
        ''', level_rewards)

        conn.commit()
        conn.close()

    def create_user(self, username: str, start_weight: float, target_weight: float = 90.0, target_date: str = '2027-07-22') -> int:
        """Create a new user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO user_profile
            (username, start_weight, current_weight, target_weight, target_date, start_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, start_weight, start_weight, target_weight, target_date, datetime.now().isoformat()))

        user_id = cursor.lastrowid

        # Initialize streaks
        streak_types = ['weight_log', 'calorie_log', 'quest_complete']
        for streak_type in streak_types:
            cursor.execute('''
                INSERT INTO streaks (user_id, streak_type, current_streak, longest_streak)
                VALUES (?, ?, 0, 0)
            ''', (user_id, streak_type))

        conn.commit()
        conn.close()

        return user_id

    def get_user(self, user_id: int = 1) -> Dict:
        """Get user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM user_profile WHERE id = ?', (user_id,))
        user = dict(cursor.fetchone())

        conn.close()
        return user

    def add_weight_log(self, user_id: int, weight: float, notes: str = '') -> Dict:
        """Add a weight log entry and process XP/achievements"""
        conn = self.get_connection()
        cursor = conn.cursor()

        now = datetime.now()
        log_date = now.date().isoformat()
        log_time = now.time().isoformat()

        # Base XP for logging
        xp_earned = 50

        # Bonus XP for early morning logs (before 8am)
        if now.hour < 8:
            xp_earned += 25

        # Insert weight log
        cursor.execute('''
            INSERT INTO weight_logs (user_id, weight, log_date, log_time, notes, xp_earned)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, weight, log_date, log_time, notes, xp_earned))

        # Update current weight
        cursor.execute('UPDATE user_profile SET current_weight = ? WHERE id = ?', (weight, user_id))

        # Update streak
        self.update_streak(user_id, 'weight_log', log_date)

        # Update quest progress
        self.update_quest_progress(user_id, 'log_weight', log_date)

        # Add XP to user
        self.add_xp(user_id, xp_earned)

        # Check for achievements
        achievements = self.check_achievements(user_id)

        conn.commit()
        conn.close()

        return {
            'xp_earned': xp_earned,
            'new_achievements': achievements,
            'log_date': log_date
        }

    def add_xp(self, user_id: int, xp: int) -> Dict:
        """Add XP to user and handle level ups"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT total_xp, current_level FROM user_profile WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        current_xp = user_data['total_xp']
        current_level = user_data['current_level']

        new_xp = current_xp + xp

        # Check for level up
        cursor.execute('SELECT level, xp_required, title FROM level_rewards WHERE level > ? ORDER BY level', (current_level,))
        next_levels = cursor.fetchall()

        leveled_up = False
        new_level = current_level
        new_title = None

        for level_data in next_levels:
            if new_xp >= level_data['xp_required']:
                new_level = level_data['level']
                new_title = level_data['title']
                leveled_up = True
            else:
                break

        # Update user
        if leveled_up:
            cursor.execute('''
                UPDATE user_profile
                SET total_xp = ?, current_level = ?, title = ?
                WHERE id = ?
            ''', (new_xp, new_level, new_title, user_id))
        else:
            cursor.execute('UPDATE user_profile SET total_xp = ? WHERE id = ?', (new_xp, user_id))

        conn.commit()
        conn.close()

        return {
            'leveled_up': leveled_up,
            'new_level': new_level if leveled_up else current_level,
            'new_title': new_title,
            'total_xp': new_xp
        }

    def update_streak(self, user_id: int, streak_type: str, activity_date: str):
        """Update streak for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT current_streak, longest_streak, last_activity_date
            FROM streaks
            WHERE user_id = ? AND streak_type = ?
        ''', (user_id, streak_type))

        streak_data = cursor.fetchone()

        if streak_data:
            last_date = streak_data['last_activity_date']
            current_streak = streak_data['current_streak']
            longest_streak = streak_data['longest_streak']

            if last_date:
                last_date_obj = datetime.fromisoformat(last_date).date()
                activity_date_obj = datetime.fromisoformat(activity_date).date()

                # Check if consecutive days
                if (activity_date_obj - last_date_obj).days == 1:
                    current_streak += 1
                elif activity_date_obj == last_date_obj:
                    # Same day, don't update streak
                    conn.close()
                    return
                else:
                    # Streak broken
                    current_streak = 1
            else:
                current_streak = 1

            # Update longest streak
            if current_streak > longest_streak:
                longest_streak = current_streak

            cursor.execute('''
                UPDATE streaks
                SET current_streak = ?, longest_streak = ?, last_activity_date = ?
                WHERE user_id = ? AND streak_type = ?
            ''', (current_streak, longest_streak, activity_date, user_id, streak_type))

        conn.commit()
        conn.close()

    def update_quest_progress(self, user_id: int, quest_key: str, quest_date: str):
        """Update daily quest progress"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get quest details
        cursor.execute('SELECT id, xp_reward, requirement_count FROM daily_quests WHERE quest_key = ?', (quest_key,))
        quest = cursor.fetchone()

        if not quest:
            conn.close()
            return

        quest_id = quest['id']
        xp_reward = quest['xp_reward']
        requirement_count = quest['requirement_count']

        # Check if quest progress exists for today
        cursor.execute('''
            SELECT id, progress, completed
            FROM user_quest_progress
            WHERE user_id = ? AND quest_id = ? AND quest_date = ?
        ''', (user_id, quest_id, quest_date))

        progress_data = cursor.fetchone()

        if progress_data:
            if not progress_data['completed']:
                new_progress = progress_data['progress'] + 1
                completed = new_progress >= requirement_count

                cursor.execute('''
                    UPDATE user_quest_progress
                    SET progress = ?, completed = ?, completed_at = ?
                    WHERE id = ?
                ''', (new_progress, completed, datetime.now().isoformat() if completed else None, progress_data['id']))

                if completed:
                    self.add_xp(user_id, xp_reward)
        else:
            completed = requirement_count == 1
            cursor.execute('''
                INSERT INTO user_quest_progress
                (user_id, quest_id, progress, completed, quest_date, completed_at)
                VALUES (?, ?, 1, ?, ?, ?)
            ''', (user_id, quest_id, completed, quest_date, datetime.now().isoformat() if completed else None))

            if completed:
                self.add_xp(user_id, xp_reward)

        conn.commit()
        conn.close()

    def check_achievements(self, user_id: int) -> List[Dict]:
        """Check and unlock new achievements"""
        conn = self.get_connection()
        cursor = conn.cursor()

        new_achievements = []

        # Get all achievements
        cursor.execute('SELECT * FROM achievements')
        all_achievements = cursor.fetchall()

        # Get user stats
        user = self.get_user(user_id)

        cursor.execute('SELECT COUNT(*) as count FROM weight_logs WHERE user_id = ?', (user_id,))
        weight_log_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM progress_photos WHERE user_id = ?', (user_id,))
        photo_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM journal_entries WHERE user_id = ?', (user_id,))
        journal_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM calorie_logs WHERE user_id = ?', (user_id,))
        calorie_count = cursor.fetchone()['count']

        cursor.execute('''
            SELECT current_streak FROM streaks
            WHERE user_id = ? AND streak_type = 'weight_log'
        ''', (user_id,))
        streak_data = cursor.fetchone()
        current_streak = streak_data['current_streak'] if streak_data else 0

        # Calculate weight gained
        weight_gained = user['current_weight'] - user['start_weight'] if user['start_weight'] else 0

        # Calculate progress percentage
        total_to_gain = user['target_weight'] - user['start_weight'] if user['start_weight'] else 0
        progress_percent = (weight_gained / total_to_gain * 100) if total_to_gain > 0 else 0

        for achievement in all_achievements:
            # Check if already unlocked
            cursor.execute('''
                SELECT id FROM user_achievements
                WHERE user_id = ? AND achievement_id = ?
            ''', (user_id, achievement['id']))

            if cursor.fetchone():
                continue

            # Check requirements
            unlocked = False
            req_type = achievement['requirement_type']
            req_value = achievement['requirement_value']

            if req_type == 'weight_logs' and weight_log_count >= req_value:
                unlocked = True
            elif req_type == 'photos' and photo_count >= req_value:
                unlocked = True
            elif req_type == 'journals' and journal_count >= req_value:
                unlocked = True
            elif req_type == 'calories' and calorie_count >= req_value:
                unlocked = True
            elif req_type == 'streak_days' and current_streak >= req_value:
                unlocked = True
            elif req_type == 'weight_gained' and weight_gained >= req_value:
                unlocked = True
            elif req_type == 'progress_percent' and progress_percent >= req_value:
                unlocked = True
            elif req_type == 'level' and user['current_level'] >= req_value:
                unlocked = True
            elif req_type == 'goal_complete' and user['current_weight'] >= user['target_weight']:
                unlocked = True

            if unlocked:
                cursor.execute('''
                    INSERT INTO user_achievements (user_id, achievement_id, seen)
                    VALUES (?, ?, 0)
                ''', (user_id, achievement['id']))

                # Award XP
                self.add_xp(user_id, achievement['xp_reward'])

                new_achievements.append(dict(achievement))

        conn.commit()
        conn.close()

        return new_achievements

    def get_dashboard_data(self, user_id: int = 1) -> Dict:
        """Get all data for the dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # User profile
        user = self.get_user(user_id)

        # Weight logs (last 30)
        cursor.execute('''
            SELECT * FROM weight_logs
            WHERE user_id = ?
            ORDER BY log_date DESC, log_time DESC
            LIMIT 30
        ''', (user_id,))
        weight_logs = [dict(row) for row in cursor.fetchall()]

        # Streaks
        cursor.execute('SELECT * FROM streaks WHERE user_id = ?', (user_id,))
        streaks = {row['streak_type']: dict(row) for row in cursor.fetchall()}

        # Today's quests
        today = datetime.now().date().isoformat()
        cursor.execute('''
            SELECT dq.*, COALESCE(uqp.progress, 0) as progress,
                   COALESCE(uqp.completed, 0) as completed
            FROM daily_quests dq
            LEFT JOIN user_quest_progress uqp
                ON dq.id = uqp.quest_id
                AND uqp.user_id = ?
                AND uqp.quest_date = ?
        ''', (user_id, today))
        quests = [dict(row) for row in cursor.fetchall()]

        # Recent achievements (last 5 unlocked)
        cursor.execute('''
            SELECT a.*, ua.unlocked_at, ua.seen
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.id
            WHERE ua.user_id = ?
            ORDER BY ua.unlocked_at DESC
            LIMIT 5
        ''', (user_id,))
        recent_achievements = [dict(row) for row in cursor.fetchall()]

        # Calculate stats
        weight_gained = user['current_weight'] - user['start_weight'] if user['start_weight'] else 0
        total_to_gain = user['target_weight'] - user['start_weight'] if user['start_weight'] else 0
        progress_percent = (weight_gained / total_to_gain * 100) if total_to_gain > 0 else 0

        # Days until target
        target_date = datetime.fromisoformat(user['target_date'])
        days_left = (target_date - datetime.now()).days

        # Required weekly gain
        weeks_left = days_left / 7
        remaining_weight = user['target_weight'] - user['current_weight']
        required_weekly_gain = remaining_weight / weeks_left if weeks_left > 0 else 0

        # Next level info
        cursor.execute('''
            SELECT * FROM level_rewards
            WHERE level > ?
            ORDER BY level
            LIMIT 1
        ''', (user['current_level'],))
        next_level = dict(cursor.fetchone()) if cursor.fetchone() else None

        # Calculate power level
        power_level = self.calculate_power_level(user, streaks, weight_gained)

        conn.close()

        return {
            'user': user,
            'weight_logs': weight_logs,
            'streaks': streaks,
            'quests': quests,
            'recent_achievements': recent_achievements,
            'stats': {
                'weight_gained': round(weight_gained, 2),
                'progress_percent': round(progress_percent, 2),
                'days_left': days_left,
                'required_weekly_gain': round(required_weekly_gain, 2),
                'power_level': power_level
            },
            'next_level': next_level
        }

    def calculate_power_level(self, user: Dict, streaks: Dict, weight_gained: float) -> int:
        """Calculate RPG-style power level"""
        power_level = 0

        # Level contributes most
        power_level += user['current_level'] * 100

        # Weight gained
        power_level += int(weight_gained * 50)

        # Streaks
        if 'weight_log' in streaks:
            power_level += streaks['weight_log']['current_streak'] * 10

        # Total XP
        power_level += user['total_xp'] // 10

        return power_level
