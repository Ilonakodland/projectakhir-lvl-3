# config.py 

import os
from typing import Dict, Any

# Bot Tokens (Use environment variables in production)
CS_TOKEN = os.getenv("CS_TOKEN", )
PRODUCT_TOKEN = os.getenv("PRODUCT_TOKEN",)

# Bot Configuration
CS_PREFIX = "!"
PRODUCT_PREFIX = "?"
CS_BOT_NAME = "SemarakBot-CS 🤖"
PRODUCT_BOT_NAME = "SemarakBot-Product 🛍️"

# Server Configuration
SERVER_NAME = "Semua Bisa Kamu Beli 🌟"
SERVER_ICON = "/images/Shopping.jpg"

# Enhanced Color Scheme with Gradients
COLORS = {
    'primary': 0x667eea,      # Beautiful gradient blue
    'secondary': 0x764ba2,    # Purple gradient
    'success': 0x00d4aa,      # Mint green
    'warning': 0xf093fb,      # Pink gradient
    'error': 0xff6b6b,        # Soft red
    'info': 0x4ecdc4,         # Turquoise
    'gold': 0xffd700,         # Gold for VIP
    'silver': 0xc0c0c0,       # Silver
    'bronze': 0xcd7f32        # Bronze
}

# Legacy color constants for backward compatibility
COLOR_PRIMARY = COLORS['primary']
COLOR_SUCCESS = COLORS['success']
COLOR_WARNING = COLORS['warning']
COLOR_ERROR = COLORS['error']
COLOR_INFO = COLORS['info']

# Enhanced Loyalty System
LOYALTY_CONFIG = {
    'points_per_question': 2,
    'points_per_purchase': 5,
    'points_per_correct_quiz': 15,
    'points_per_daily_login': 1,
    'vip_threshold': 100,
    'premium_threshold': 500,
    'vip_discount': 0.10,      # 10%
    'premium_discount': 0.20,   # 20%
    'daily_quiz_limit': 5,
    'streak_bonus_multiplier': 1.5
}

# Backward compatibility
POINTS_PER_QUESTION = LOYALTY_CONFIG['points_per_question']
POINTS_PER_PURCHASE = LOYALTY_CONFIG['points_per_purchase']
POINTS_PER_CORRECT_QUIZ = LOYALTY_CONFIG['points_per_correct_quiz']
VIP_THRESHOLD = LOYALTY_CONFIG['vip_threshold']
VIP_DISCOUNT = LOYALTY_CONFIG['vip_discount']

# Quiz Configuration
QUIZ_CONFIG = {
    'timeout_seconds': 30,
    'max_daily_attempts': 10,
    'difficulty_levels': ['easy', 'medium', 'hard'],
    'points_multiplier': {'easy': 1, 'medium': 1.5, 'hard': 2}
}

# Legacy constant
QUIZ_TIMEOUT_SECONDS = QUIZ_CONFIG['timeout_seconds']

# Rate Limiting
RATE_LIMITS = {
    'commands_per_minute': 10,
    'quiz_cooldown': 5,  # seconds
    'purchase_cooldown': 3
}

# Features Toggle
FEATURES = {
    'achievements': True,
    'daily_rewards': True,
    'leaderboard': True,
    'statistics': True,
    'notifications': True,
    'auto_role_assignment': True
}

# Emojis for Enhanced UI
EMOJIS = {
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '⏳',
    'star': '⭐',
    'crown': '👑',
    'gem': '💎',
    'fire': '🔥',
    'rocket': '🚀',
    'trophy': '🏆',
    'medal': '🏅',
    'gift': '🎁',
    'money': '💰',
    'cart': '🛒',
    'package': '📦',
    'heart': '❤️',
    'thumbs_up': '👍',
    'celebration': '🎉'
}

# Achievement System
ACHIEVEMENTS = {
    'first_purchase': {
        'name': 'First Timer',
        'description': 'Made your first purchase!',
        'emoji': '🎯',
        'points': 50
    },
    'quiz_master': {
        'name': 'Quiz Master',
        'description': 'Answered 10 quizzes correctly',
        'emoji': '🧠',
        'points': 100
    },
    'loyal_customer': {
        'name': 'Loyal Customer',
        'description': 'Reached 500 loyalty points',
        'emoji': '👑',
        'points': 200
    },
    'streak_champion': {
        'name': 'Streak Champion',
        'description': 'Maintained a 7-day activity streak',
        'emoji': '🔥',
        'points': 150
    }
}

# Database Configuration
DATABASE_CONFIG = {
    'backup_interval': 3600,  # 1 hour
    'max_history_length': 1000,
    'auto_cleanup': True
}
