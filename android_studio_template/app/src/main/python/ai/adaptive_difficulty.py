"""
MEMORA Adaptive Difficulty Module - Phase 5
Rule-based difficulty adaptation based on recent player performance.

ARCHITECTURE NOTE:
This module implements a rule-based heuristic approach to simulate ML-based
difficulty adaptation. For the prototype, we use simple accuracy thresholds
to adjust difficulty levels.

In a production system with sufficient historical data, this could be replaced
with a trained ML classifier (e.g., scikit-learn logistic regression or random
forest) trained on features like:
  - Recent accuracy (last N games)
  - Average reaction time trends
  - Number of moves per game
  - Time trends (progression over days/weeks)

The rule-based approach is transparent, maintainable, and performs well for
initial user sessions where data is sparse.
"""

# ============================================================
# DIFFICULTY ADAPTATION LOGIC
# ============================================================

def get_next_difficulty(recent_logs):
    """
    Determine the next difficulty level based on recent game performance.
    
    Args:
        recent_logs: List of ActivityLog objects or dicts with at minimum:
                     - accuracy (float 0-100)
                     - game_type (str)
    
    Returns:
        str: One of "easy", "medium", "hard"
    
    Rules:
        - If < 3 sessions: return "easy" (start gentle)
        - Else: calculate average accuracy of last 3 sessions
            - If avg >= 80%: "hard" (user is mastering the game)
            - If avg >= 50%: "medium" (user is improving)
            - Else: "easy" (user needs more practice)
    """
    
    if not recent_logs or len(recent_logs) < 3:
        return "easy"
    
    # Take only the last 3 sessions
    recent_sessions = recent_logs[:3]
    
    # Calculate average accuracy
    accuracies = []
    for log in recent_sessions:
        if hasattr(log, 'accuracy'):
            # SQLAlchemy object
            accuracies.append(log.accuracy)
        elif isinstance(log, dict) and 'accuracy' in log:
            # Dictionary
            accuracies.append(log['accuracy'])
    
    if not accuracies:
        return "easy"
    
    avg_accuracy = sum(accuracies) / len(accuracies)
    
    # Determine difficulty based on accuracy thresholds
    if avg_accuracy >= 80:
        return "hard"
    elif avg_accuracy >= 50:
        return "medium"
    else:
        return "easy"


def get_difficulty_settings(difficulty, game_type):
    """
    Get game-specific settings for the given difficulty level.
    
    Args:
        difficulty: str, one of "easy", "medium", "hard"
        game_type: str, one of "memory_match", "attention_test"
    
    Returns:
        dict: Game-specific configuration
            For memory_match: {"pairs": <int>}
            For attention_test: {"rounds": <int>, "grid_size": <int>}
    
    Examples:
        get_difficulty_settings("medium", "memory_match")
            -> {"pairs": 6}
        
        get_difficulty_settings("hard", "attention_test")
            -> {"rounds": 10, "grid_size": 9}
    """
    
    if game_type == "memory_match":
        settings = {
            "easy": {"pairs": 4},
            "medium": {"pairs": 6},
            "hard": {"pairs": 8}
        }
        return settings.get(difficulty, settings["medium"])
    
    elif game_type == "attention_test":
        settings = {
            "easy": {"rounds": 6, "grid_size": 4},
            "medium": {"rounds": 8, "grid_size": 6},
            "hard": {"rounds": 10, "grid_size": 9}
        }
        return settings.get(difficulty, settings["medium"])
    
    else:
        # Unknown game type, return medium defaults
        return {"error": f"Unknown game_type: {game_type}"}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_difficulty_badge_emoji(difficulty):
    """Return an emoji badge for the given difficulty level"""
    badges = {
        "easy": "🟢 Easy",
        "medium": "🟡 Medium",
        "hard": "🔴 Hard"
    }
    return badges.get(difficulty, "🟡 Medium")
