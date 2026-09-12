"""
MEMORA Games Module - Phase 4
Handles game routes and result logging
"""

from flask import Blueprint, render_template, request, jsonify, session
from models.models import db, ActivityLog, User
from datetime import datetime

games_bp = Blueprint('games', __name__)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def login_required_json():
    """Check if user is logged in, return (user_id, error_response) tuple"""
    user_id = session.get('user_id')
    if not user_id:
        return None, ({"error": "Unauthorized"}, 401)
    return user_id, None

# ============================================================
# GAME ROUTES
# ============================================================

@games_bp.route('/games', methods=['GET'])
def games_hub():
    """Display games hub with available games"""
    user_id = session.get('user_id')
    if not user_id:
        return {}, 302  # This won't work, need to use redirect
    
    user = User.query.get(user_id)
    return render_template('games_hub.html', user=user)


@games_bp.route('/game/memory-match', methods=['GET'])
def memory_match_game():
    """Display memory match game"""
    user_id = session.get('user_id')
    if not user_id:
        return {}, 302
    
    user = User.query.get(user_id)
    return render_template('game_memory_match.html', user=user)


@games_bp.route('/game/attention-test', methods=['GET'])
def attention_test_game():
    """Display attention test game"""
    user_id = session.get('user_id')
    if not user_id:
        return {}, 302
    
    user = User.query.get(user_id)
    return render_template('game_attention_test.html', user=user)


# ============================================================
# GAME LOGGING API
# ============================================================

@games_bp.route('/api/games/log', methods=['POST'])
def log_game_result():
    """
    Log a game result to ActivityLog
    
    Expected JSON body:
    {
        "game_type": "memory_match" | "attention_test",
        "score": <int>,
        "accuracy": <float 0-100>,
        "time_taken": <float seconds>,
        "difficulty": "easy" | "medium" | "hard"
    }
    """
    user_id, error = login_required_json()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['game_type', 'score', 'accuracy', 'time_taken', 'difficulty']
        if not all(field in data for field in required_fields):
            return {"error": f"Missing required fields. Expected: {required_fields}"}, 400
        
        # Create ActivityLog entry
        log_entry = ActivityLog(
            user_id=user_id,
            game_type=data['game_type'],
            score=int(data['score']),
            accuracy=float(data['accuracy']),
            time_taken=float(data['time_taken']),
            difficulty=data['difficulty'],
            timestamp=datetime.utcnow()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry.to_dict(), 201
    
    except ValueError as e:
        return {"error": f"Invalid data type: {str(e)}"}, 400
    except Exception as e:
        db.session.rollback()
        return {"error": f"Server error: {str(e)}"}, 500
