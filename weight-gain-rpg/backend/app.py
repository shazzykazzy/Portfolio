"""
Weight Gain RPG - Flask Backend
Epic gamified weight tracking API
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database import Database
from datetime import datetime, timedelta
import os
import base64
from pathlib import Path

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Initialize database
db = Database()

# Ensure upload directory exists
UPLOAD_DIR = Path('../frontend/static/uploads')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def initialize_user():
    """Initialize a new user"""
    data = request.json
    username = data.get('username', 'Player')
    start_weight = float(data.get('start_weight'))
    target_weight = float(data.get('target_weight', 90.0))
    target_date = data.get('target_date', '2027-07-22')

    try:
        user_id = db.create_user(username, start_weight, target_weight, target_date)
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': f'Welcome, {username}! Your journey begins! 🎮'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get complete dashboard data"""
    user_id = request.args.get('user_id', 1, type=int)

    try:
        data = db.get_dashboard_data(user_id)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/weight', methods=['POST'])
def log_weight():
    """Log a new weight entry"""
    data = request.json
    user_id = data.get('user_id', 1)
    weight = float(data.get('weight'))
    notes = data.get('notes', '')

    try:
        result = db.add_weight_log(user_id, weight, notes)
        return jsonify({
            'success': True,
            'message': f'Weight logged! +{result["xp_earned"]} XP earned! 💪',
            'xp_earned': result['xp_earned'],
            'new_achievements': result['new_achievements']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/weight/history', methods=['GET'])
def get_weight_history():
    """Get weight history"""
    user_id = request.args.get('user_id', 1, type=int)
    limit = request.args.get('limit', 100, type=int)

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM weight_logs
        WHERE user_id = ?
        ORDER BY log_date DESC, log_time DESC
        LIMIT ?
    ''', (user_id, limit))

    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        'success': True,
        'logs': logs
    })


@app.route('/api/photo', methods=['POST'])
def upload_photo():
    """Upload a progress photo"""
    user_id = request.form.get('user_id', 1)
    caption = request.form.get('caption', '')

    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No photo provided'}), 400

    photo = request.files['photo']

    # Save photo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'progress_{user_id}_{timestamp}.jpg'
    photo_path = UPLOAD_DIR / filename
    photo.save(photo_path)

    # Get current weight
    user = db.get_user(user_id)
    current_weight = user['current_weight']

    # Save to database
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO progress_photos
        (user_id, photo_path, weight_at_photo, upload_date, caption, xp_earned)
        VALUES (?, ?, ?, ?, ?, 100)
    ''', (user_id, f'uploads/{filename}', current_weight, datetime.now().date().isoformat(), caption))

    conn.commit()

    # Update quest progress
    db.update_quest_progress(user_id, 'upload_photo', datetime.now().date().isoformat())

    # Add XP
    xp_result = db.add_xp(user_id, 100)

    # Check achievements
    achievements = db.check_achievements(user_id)

    conn.close()

    return jsonify({
        'success': True,
        'message': 'Photo uploaded! +100 XP! 📸',
        'xp_earned': 100,
        'photo_path': f'uploads/{filename}',
        'new_achievements': achievements,
        'level_up': xp_result
    })


@app.route('/api/photos', methods=['GET'])
def get_photos():
    """Get progress photos"""
    user_id = request.args.get('user_id', 1, type=int)

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM progress_photos
        WHERE user_id = ?
        ORDER BY upload_date DESC
    ''', (user_id,))

    photos = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        'success': True,
        'photos': photos
    })


@app.route('/api/calories', methods=['POST'])
def log_calories():
    """Log calorie intake"""
    data = request.json
    user_id = data.get('user_id', 1)
    calories = int(data.get('calories'))
    target_calories = data.get('target_calories')

    conn = db.get_connection()
    cursor = conn.cursor()

    log_date = datetime.now().date().isoformat()
    xp_earned = 30

    # Bonus XP if target hit
    if target_calories and calories >= target_calories:
        xp_earned += 50

    cursor.execute('''
        INSERT INTO calorie_logs
        (user_id, log_date, calories, target_calories, xp_earned)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, log_date, calories, target_calories, xp_earned))

    conn.commit()

    # Update quests
    db.update_quest_progress(user_id, 'log_calories', log_date)
    if target_calories and calories >= target_calories:
        db.update_quest_progress(user_id, 'hit_calorie_target', log_date)

    # Add XP
    xp_result = db.add_xp(user_id, xp_earned)

    # Check achievements
    achievements = db.check_achievements(user_id)

    conn.close()

    return jsonify({
        'success': True,
        'message': f'Calories logged! +{xp_earned} XP! 🍔',
        'xp_earned': xp_earned,
        'new_achievements': achievements,
        'level_up': xp_result
    })


@app.route('/api/journal', methods=['POST'])
def add_journal():
    """Add journal entry"""
    data = request.json
    user_id = data.get('user_id', 1)
    entry_text = data.get('entry_text')
    mood = data.get('mood', 'neutral')

    conn = db.get_connection()
    cursor = conn.cursor()

    entry_date = datetime.now().date().isoformat()
    xp_earned = 40

    cursor.execute('''
        INSERT INTO journal_entries
        (user_id, entry_date, entry_text, mood, xp_earned)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, entry_date, entry_text, mood, xp_earned))

    conn.commit()

    # Update quest
    db.update_quest_progress(user_id, 'write_journal', entry_date)

    # Add XP
    xp_result = db.add_xp(user_id, xp_earned)

    # Check achievements
    achievements = db.check_achievements(user_id)

    conn.close()

    return jsonify({
        'success': True,
        'message': 'Journal entry saved! +40 XP! 📝',
        'xp_earned': xp_earned,
        'new_achievements': achievements,
        'level_up': xp_result
    })


@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Get all achievements (unlocked and locked)"""
    user_id = request.args.get('user_id', 1, type=int)

    conn = db.get_connection()
    cursor = conn.cursor()

    # Get all achievements with unlock status
    cursor.execute('''
        SELECT a.*,
               CASE WHEN ua.id IS NOT NULL THEN 1 ELSE 0 END as unlocked,
               ua.unlocked_at
        FROM achievements a
        LEFT JOIN user_achievements ua
            ON a.id = ua.achievement_id AND ua.user_id = ?
        ORDER BY a.rarity, a.name
    ''', (user_id,))

    achievements = [dict(row) for row in cursor.fetchall()]

    # Group by rarity
    grouped = {
        'common': [],
        'rare': [],
        'epic': [],
        'legendary': []
    }

    for ach in achievements:
        grouped[ach['rarity']].append(ach)

    conn.close()

    return jsonify({
        'success': True,
        'achievements': grouped,
        'all': achievements
    })


@app.route('/api/quests', methods=['GET'])
def get_quests():
    """Get today's quests"""
    user_id = request.args.get('user_id', 1, type=int)
    today = datetime.now().date().isoformat()

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT dq.*,
               COALESCE(uqp.progress, 0) as progress,
               COALESCE(uqp.completed, 0) as completed
        FROM daily_quests dq
        LEFT JOIN user_quest_progress uqp
            ON dq.id = uqp.quest_id
            AND uqp.user_id = ?
            AND uqp.quest_date = ?
    ''', (user_id, today))

    quests = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        'success': True,
        'quests': quests
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get detailed stats for RPG dashboard"""
    user_id = request.args.get('user_id', 1, type=int)

    user = db.get_user(user_id)

    conn = db.get_connection()
    cursor = conn.cursor()

    # Weight stats
    cursor.execute('SELECT COUNT(*) as count FROM weight_logs WHERE user_id = ?', (user_id,))
    total_logs = cursor.fetchone()['count']

    cursor.execute('''
        SELECT AVG(weight) as avg_weight
        FROM (
            SELECT weight FROM weight_logs
            WHERE user_id = ?
            ORDER BY log_date DESC, log_time DESC
            LIMIT 7
        )
    ''', (user_id,))
    avg_last_7_days = cursor.fetchone()['avg_weight'] or 0

    # Streak stats
    cursor.execute('''
        SELECT streak_type, current_streak, longest_streak
        FROM streaks WHERE user_id = ?
    ''', (user_id,))
    streaks = {row['streak_type']: dict(row) for row in cursor.fetchall()}

    # Achievement stats
    cursor.execute('''
        SELECT COUNT(*) as unlocked FROM user_achievements WHERE user_id = ?
    ''', (user_id,))
    achievements_unlocked = cursor.fetchone()['unlocked']

    cursor.execute('SELECT COUNT(*) as total FROM achievements')
    achievements_total = cursor.fetchone()['total']

    # Calculate RPG stats
    weight_gained = user['current_weight'] - user['start_weight'] if user['start_weight'] else 0
    total_to_gain = user['target_weight'] - user['start_weight'] if user['start_weight'] else 0
    progress_percent = (weight_gained / total_to_gain * 100) if total_to_gain > 0 else 0

    # Power level
    power_level = db.calculate_power_level(user, streaks, weight_gained)

    # Days active
    if user['start_date']:
        start = datetime.fromisoformat(user['start_date'])
        days_active = (datetime.now() - start).days
    else:
        days_active = 0

    conn.close()

    return jsonify({
        'success': True,
        'stats': {
            'STR': 50 + (total_logs * 2),  # Strength based on logging consistency
            'MASS': round(user['current_weight'], 1),
            'GOAL': user['target_weight'],
            'MOMENTUM': round(weight_gained / max(days_active / 30, 1), 2) if days_active > 0 else 0,  # kg per month
            'CONSISTENCY': streaks.get('weight_log', {}).get('current_streak', 0),
            'DEDICATION': days_active,
            'POWER_LEVEL': power_level,
            'PROGRESS_PCT': round(progress_percent, 1),
            'ACHIEVEMENTS': f'{achievements_unlocked}/{achievements_total}'
        }
    })


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get personal leaderboard (compare with past self)"""
    user_id = request.args.get('user_id', 1, type=int)

    conn = db.get_connection()
    cursor = conn.cursor()

    # Get milestones
    cursor.execute('''
        SELECT log_date, weight, notes
        FROM weight_logs
        WHERE user_id = ?
        ORDER BY weight ASC
        LIMIT 10
    ''', (user_id,))

    milestones = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'success': True,
        'milestones': milestones
    })


@app.route('/api/mark-achievement-seen', methods=['POST'])
def mark_achievement_seen():
    """Mark achievement notification as seen"""
    data = request.json
    user_id = data.get('user_id', 1)
    achievement_id = data.get('achievement_id')

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE user_achievements
        SET seen = 1
        WHERE user_id = ? AND achievement_id = ?
    ''', (user_id, achievement_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/unseen-achievements', methods=['GET'])
def get_unseen_achievements():
    """Get unseen achievements for popup notifications"""
    user_id = request.args.get('user_id', 1, type=int)

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT a.*, ua.unlocked_at
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = ? AND ua.seen = 0
        ORDER BY ua.unlocked_at DESC
    ''', (user_id,))

    achievements = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        'success': True,
        'achievements': achievements
    })


if __name__ == '__main__':
    # Check if user exists, if not prompt for initialization
    try:
        user = db.get_user(1)
        print(f"\n🎮 Welcome back, {user['username']}! 🎮")
        print(f"💪 Current Level: {user['current_level']} - {user['title']}")
        print(f"⚖️  Current Weight: {user['current_weight']}kg")
        print(f"🎯 Target: {user['target_weight']}kg by {user['target_date']}")
        print(f"⭐ Total XP: {user['total_xp']}\n")
    except:
        print("\n🎮 Welcome to Weight Gain RPG! 🎮")
        print("Visit http://localhost:5000 to start your journey!\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
