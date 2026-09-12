"""
MEMORA Progress Module - Phase 5-6
Handles progress tracking, adaptive difficulty endpoints, and caregiver dashboard data
"""

from flask import Blueprint, request, jsonify, session
from models.models import db, ActivityLog
from ai.adaptive_difficulty import get_next_difficulty, get_difficulty_settings

progress_bp = Blueprint('progress', __name__, url_prefix='/api')

# ============================================================
# ADAPTIVE DIFFICULTY ENDPOINT
# ============================================================

@progress_bp.route('/difficulty/<int:user_id>', methods=['GET'])
def get_user_difficulty(user_id):
    """
    Get the next recommended difficulty for a user based on recent performance.
    
    Returns JSON:
    {
        "user_id": <int>,
        "difficulty": "easy|medium|hard",
        "settings": {
            "pairs": <int>  [for memory_match]
            OR
            "rounds": <int>, "grid_size": <int>  [for attention_test]
        }
    }
    """
    
    try:
        # Fetch user's last 3 game sessions, ordered by most recent first
        recent_logs = ActivityLog.query.filter_by(user_id=user_id)\
            .order_by(ActivityLog.timestamp.desc())\
            .limit(3)\
            .all()
        
        # Determine next difficulty based on recent performance
        next_difficulty = get_next_difficulty(recent_logs)
        
        # For now, return a combined settings object for both game types
        # Frontend will select which settings to use based on game_type
        response = {
            "user_id": user_id,
            "difficulty": next_difficulty,
            "settings": {
                "memory_match": get_difficulty_settings(next_difficulty, "memory_match"),
                "attention_test": get_difficulty_settings(next_difficulty, "attention_test")
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return {"error": f"Failed to fetch difficulty: {str(e)}"}, 500


# ============================================================
# PROGRESS DATA ENDPOINT (For Dashboard)
# ============================================================

@progress_bp.route('/progress/<int:user_id>', methods=['GET'])
def get_user_progress(user_id):
    """
    Get all game activity for a user, ordered by timestamp.
    
    Returns JSON list of activity logs:
    [
        {
            "timestamp": "2026-09-12T10:30:45.123456",
            "game_type": "memory_match",
            "score": 850,
            "accuracy": 91.5,
            "difficulty": "medium"
        },
        ...
    ]
    """
    
    try:
        # Fetch all game sessions for this user, ordered by timestamp ascending
        # (oldest first, so charts show progression over time)
        logs = ActivityLog.query.filter_by(user_id=user_id)\
            .order_by(ActivityLog.timestamp.asc())\
            .all()
        
        # Transform to list of dicts with required fields
        progress_data = [
            {
                "timestamp": log.timestamp.isoformat(),
                "game_type": log.game_type,
                "score": log.score,
                "accuracy": log.accuracy,
                "difficulty": log.difficulty
            }
            for log in logs
        ]
        
        return jsonify(progress_data), 200
    
    except Exception as e:
        return {"error": f"Failed to fetch progress: {str(e)}"}, 500
