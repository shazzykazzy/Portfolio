/**
 * Weight Gain RPG - Main Application JavaScript
 * Epic gamified weight tracking with RPG mechanics
 */

// Global State
let userData = null;
let dashboardData = null;
let weightChart = null;

// API Base URL
const API_URL = '';

// Initialize app on page load
document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    checkUserInitialized();
});

/**
 * Initialize Particles.js background
 */
function initParticles() {
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: '#7C3AED' },
                shape: { type: 'circle' },
                opacity: {
                    value: 0.5,
                    random: true,
                    anim: { enable: true, speed: 1, opacity_min: 0.1 }
                },
                size: {
                    value: 3,
                    random: true,
                    anim: { enable: true, speed: 2, size_min: 0.1 }
                },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: '#EC4899',
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: 'none',
                    random: false,
                    straight: false,
                    out_mode: 'out',
                    bounce: false
                }
            },
            interactivity: {
                detect_on: 'canvas',
                events: {
                    onhover: { enable: true, mode: 'repulse' },
                    onclick: { enable: true, mode: 'push' },
                    resize: true
                },
                modes: {
                    repulse: { distance: 100, duration: 0.4 },
                    push: { particles_nb: 4 }
                }
            },
            retina_detect: true
        });
    }
}

/**
 * Check if user is initialized
 */
async function checkUserInitialized() {
    try {
        const response = await fetch(`${API_URL}/api/dashboard?user_id=1`);
        const result = await response.json();

        if (result.success && result.data.user) {
            userData = result.data.user;
            loadDashboard();
        } else {
            showInitModal();
        }
    } catch (error) {
        // User doesn't exist, show init modal
        showInitModal();
    }
}

/**
 * Show initialization modal
 */
function showInitModal() {
    document.getElementById('initModal').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');

    document.getElementById('initForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value || 'Player';
        const startWeight = parseFloat(document.getElementById('startWeight').value);
        const targetWeight = parseFloat(document.getElementById('targetWeight').value);
        const targetDate = document.getElementById('targetDate').value;

        try {
            const response = await fetch(`${API_URL}/api/init`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username,
                    start_weight: startWeight,
                    target_weight: targetWeight,
                    target_date: targetDate
                })
            });

            const result = await response.json();

            if (result.success) {
                document.getElementById('initModal').classList.add('hidden');
                showToast(result.message, 'success');
                triggerConfetti();
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showToast('Error initializing user: ' + result.error, 'error');
            }
        } catch (error) {
            showToast('Error: ' + error.message, 'error');
        }
    });
}

/**
 * Load main dashboard
 */
async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/api/dashboard?user_id=1`);
        const result = await response.json();

        if (!result.success) {
            showToast('Error loading dashboard', 'error');
            return;
        }

        dashboardData = result.data;
        updateDashboard();
        checkUnseenAchievements();

        document.getElementById('initModal').classList.add('hidden');
        document.getElementById('dashboard').classList.remove('hidden');
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
}

/**
 * Update dashboard UI with data
 */
function updateDashboard() {
    const { user, stats, weight_logs, streaks, quests, recent_achievements, next_level } = dashboardData;

    // Update user info
    document.getElementById('username-display').textContent = user.username;
    document.getElementById('userTitle').textContent = user.title;
    document.getElementById('levelBadge').textContent = user.current_level;
    document.getElementById('currentLevel').textContent = user.current_level;

    // Update main stats
    document.getElementById('currentWeight').textContent = user.current_weight ? user.current_weight.toFixed(1) : '--';
    document.getElementById('targetWeight').textContent = user.target_weight.toFixed(1);
    document.getElementById('progressPercent').textContent = stats.progress_percent.toFixed(1) + '%';
    document.getElementById('daysLeft').textContent = stats.days_left;

    // Update XP bar
    document.getElementById('currentXP').textContent = user.total_xp;
    if (next_level) {
        document.getElementById('nextLevelXP').textContent = next_level.xp_required;
        const xpPercent = (user.total_xp / next_level.xp_required) * 100;
        document.getElementById('xpBar').style.width = Math.min(xpPercent, 100) + '%';
    } else {
        document.getElementById('nextLevelXP').textContent = 'MAX';
        document.getElementById('xpBar').style.width = '100%';
    }

    // Update streak
    const weightStreak = streaks.weight_log || { current_streak: 0 };
    document.getElementById('streakCount').textContent = weightStreak.current_streak;
    updateStreakEmojis(weightStreak.current_streak);

    // Update required gain rate
    document.getElementById('weeklyGain').textContent = stats.required_weekly_gain.toFixed(2) + ' kg';
    document.getElementById('monthlyGain').textContent = (stats.required_weekly_gain * 4.33).toFixed(2) + ' kg';

    // Update quests
    updateQuests(quests);

    // Update achievements
    updateRecentAchievements(recent_achievements);

    // Update RPG stats
    updateRPGStats();

    // Update weight chart
    updateWeightChart(weight_logs);
}

/**
 * Update RPG stats
 */
async function updateRPGStats() {
    try {
        const response = await fetch(`${API_URL}/api/stats?user_id=1`);
        const result = await response.json();

        if (!result.success) return;

        const stats = result.stats;

        // Update stat values
        document.getElementById('statSTR').textContent = stats.STR;
        document.getElementById('statMASS').textContent = stats.MASS;
        document.getElementById('statMOMENTUM').textContent = stats.MOMENTUM;
        document.getElementById('statCONSISTENCY').textContent = stats.CONSISTENCY;
        document.getElementById('statDEDICATION').textContent = stats.DEDICATION;
        document.getElementById('statPOWER').textContent = stats.POWER_LEVEL;

        // Update stat bars (scale to 100 for visual purposes)
        document.getElementById('barSTR').style.width = Math.min((stats.STR / 200) * 100, 100) + '%';
        document.getElementById('barMASS').style.width = Math.min((stats.MASS / 150) * 100, 100) + '%';
        document.getElementById('barMOMENTUM').style.width = Math.min((stats.MOMENTUM / 5) * 100, 100) + '%';
        document.getElementById('barCONSISTENCY').style.width = Math.min((stats.CONSISTENCY / 100) * 100, 100) + '%';
        document.getElementById('barDEDICATION').style.width = Math.min((stats.DEDICATION / 365) * 100, 100) + '%';
        document.getElementById('barPOWER').style.width = Math.min((stats.POWER_LEVEL / 10000) * 100, 100) + '%';

    } catch (error) {
        console.error('Error updating RPG stats:', error);
    }
}

/**
 * Update streak emojis
 */
function updateStreakEmojis(streak) {
    let emojis = '';
    if (streak === 0) {
        emojis = '💤';
    } else if (streak < 7) {
        emojis = '🔥'.repeat(Math.min(streak, 5));
    } else if (streak < 30) {
        emojis = '🔥🔥🔥⚡';
    } else if (streak < 100) {
        emojis = '🔥🔥🔥⚡⚡';
    } else {
        emojis = '🔥🔥🔥⚡⚡💎';
    }
    document.getElementById('streakEmojis').textContent = emojis;
}

/**
 * Update quests display
 */
function updateQuests(quests) {
    const questList = document.getElementById('questList');
    questList.innerHTML = '';

    if (!quests || quests.length === 0) {
        questList.innerHTML = '<div class="text-center text-gray-500 py-4">No quests available</div>';
        return;
    }

    quests.forEach(quest => {
        const questEl = document.createElement('div');
        questEl.className = 'flex items-center gap-4 p-4 glass-card rounded-xl hover-scale';

        const isCompleted = quest.completed === 1;

        questEl.innerHTML = `
            <input type="checkbox" class="quest-checkbox" ${isCompleted ? 'checked disabled' : ''}>
            <div class="flex-1">
                <div class="font-bold ${isCompleted ? 'line-through text-gray-500' : ''}">${quest.name}</div>
                <div class="text-sm text-gray-400">${quest.description}</div>
            </div>
            <div class="text-right">
                <div class="text-green-400 font-bold">+${quest.xp_reward} XP</div>
                <div class="text-3xl">${quest.icon}</div>
            </div>
        `;

        questList.appendChild(questEl);
    });
}

/**
 * Update recent achievements
 */
function updateRecentAchievements(achievements) {
    const achievementsList = document.getElementById('achievementsList');
    achievementsList.innerHTML = '';

    if (!achievements || achievements.length === 0) {
        achievementsList.innerHTML = '<div class="text-center text-gray-500 py-4">No achievements yet!</div>';
        return;
    }

    achievements.forEach(ach => {
        const achEl = document.createElement('div');
        achEl.className = `glass-card rounded-xl p-4 hover-scale rarity-${ach.rarity}`;

        achEl.innerHTML = `
            <div class="flex items-center gap-3">
                <div class="text-4xl">${ach.icon}</div>
                <div class="flex-1">
                    <div class="font-bold">${ach.name}</div>
                    <div class="text-xs text-gray-400">${ach.description}</div>
                </div>
            </div>
        `;

        achievementsList.appendChild(achEl);
    });
}

/**
 * Update weight chart
 */
function updateWeightChart(weightLogs) {
    const ctx = document.getElementById('weightChart');
    if (!ctx) return;

    // Prepare data
    const reversedLogs = [...weightLogs].reverse();
    const labels = reversedLogs.map(log => {
        const date = new Date(log.log_date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const weights = reversedLogs.map(log => log.weight);

    // Destroy existing chart
    if (weightChart) {
        weightChart.destroy();
    }

    // Create gradient
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(124, 58, 237, 0.8)');
    gradient.addColorStop(1, 'rgba(236, 72, 153, 0.2)');

    // Create chart
    weightChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Weight (kg)',
                data: weights,
                borderColor: '#EC4899',
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#EC4899',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleColor: '#EC4899',
                    bodyColor: '#fff',
                    borderColor: '#7C3AED',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#9CA3AF' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#9CA3AF' }
                }
            }
        }
    });
}

/**
 * Show log weight modal
 */
function showLogWeightModal() {
    document.getElementById('logWeightModal').classList.remove('hidden');
    document.getElementById('weightInput').focus();
}

/**
 * Hide log weight modal
 */
function hideLogWeightModal() {
    document.getElementById('logWeightModal').classList.add('hidden');
    document.getElementById('logWeightForm').reset();
}

/**
 * Log weight form submission
 */
document.getElementById('logWeightForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const weight = parseFloat(document.getElementById('weightInput').value);
    const notes = document.getElementById('weightNotes').value;

    try {
        const response = await fetch(`${API_URL}/api/weight`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 1,
                weight: weight,
                notes: notes
            })
        });

        const result = await response.json();

        if (result.success) {
            hideLogWeightModal();
            showToast(result.message, 'success');
            triggerConfetti();

            // Check for new achievements
            if (result.new_achievements && result.new_achievements.length > 0) {
                result.new_achievements.forEach((ach, index) => {
                    setTimeout(() => {
                        showAchievementPopup(ach);
                    }, (index + 1) * 1000);
                });
            }

            // Reload dashboard
            setTimeout(() => loadDashboard(), 500);
        } else {
            showToast('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'error');
    }
});

/**
 * Show achievement popup
 */
function showAchievementPopup(achievement) {
    document.getElementById('achievementIcon').textContent = achievement.icon;
    document.getElementById('achievementName').textContent = achievement.name;
    document.getElementById('achievementDesc').textContent = achievement.description;
    document.getElementById('achievementXP').textContent = achievement.xp_reward;

    const popup = document.getElementById('achievementPopup');
    popup.classList.remove('hidden');

    triggerConfetti();

    setTimeout(() => {
        popup.classList.add('hidden');
    }, 5000);
}

/**
 * Show level up popup
 */
function showLevelUpPopup(level, title) {
    document.getElementById('newLevel').textContent = level;
    document.getElementById('newTitle').textContent = title;
    document.getElementById('levelUpPopup').classList.remove('hidden');

    triggerConfetti();
    triggerConfetti();
    triggerConfetti();
}

/**
 * Hide level up popup
 */
function hideLevelUpPopup() {
    document.getElementById('levelUpPopup').classList.add('hidden');
}

/**
 * Check for unseen achievements
 */
async function checkUnseenAchievements() {
    try {
        const response = await fetch(`${API_URL}/api/unseen-achievements?user_id=1`);
        const result = await response.json();

        if (result.success && result.achievements.length > 0) {
            result.achievements.forEach((ach, index) => {
                setTimeout(() => {
                    showAchievementPopup(ach);
                    // Mark as seen
                    fetch(`${API_URL}/api/mark-achievement-seen`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: 1,
                            achievement_id: ach.id
                        })
                    });
                }, (index + 1) * 2000);
            });
        }
    } catch (error) {
        console.error('Error checking achievements:', error);
    }
}

/**
 * Trigger confetti animation
 */
function triggerConfetti() {
    if (typeof confetti !== 'undefined') {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#7C3AED', '#EC4899', '#06B6D4', '#10B981', '#F59E0B']
        });
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    toastMessage.textContent = message;
    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

/**
 * Show photo upload modal (placeholder)
 */
function showPhotoModal() {
    showToast('Photo upload feature - Coming soon! 📸', 'info');
}

/**
 * Show calorie modal (placeholder)
 */
function showCalorieModal() {
    showToast('Calorie logging feature - Coming soon! 🍔', 'info');
}

/**
 * Show journal modal (placeholder)
 */
function showJournalModal() {
    showToast('Journal feature - Coming soon! 📝', 'info');
}

/**
 * Show all achievements (placeholder)
 */
function showAllAchievements() {
    showToast('Achievement gallery - Coming soon! 🏆', 'info');
}
