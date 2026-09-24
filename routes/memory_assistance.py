"""
MEMORA Memory Assistance Routes - Phase 10C
Handles Memory Search and Memory Companion voice queries
"""

from flask import Blueprint, request, session, jsonify
from models.models import db, User
from utils.memory_search import normalize_query, search_patient_memory
from utils.response_generator import generate_response

memory_assistance_bp = Blueprint('memory_assistance', __name__, url_prefix='/api/memory')


# ============================================================
# AUTHORIZATION HELPERS
# ============================================================

def check_user_authenticated():
    """
    Check if user is authenticated via session.
    Returns: (user_id, error_response) where error_response is None if authenticated
    """
    user_id = session.get('user_id')
    if not user_id:
        return None, ({"error": "Unauthorized"}, 401)
    
    # Verify user still exists
    user = User.query.get(user_id)
    if not user:
        return None, ({"error": "Unauthorized"}, 401)
    
    return user_id, None


# ============================================================
# MEMORY SEARCH ENDPOINT
# ============================================================

@memory_assistance_bp.route('/search', methods=['POST'])
def search_memory():
    """
    Search patient's memory records (people, places, memories).
    
    Request body:
        {
            "query": "Who is Anil?"
        }
    
    Response:
        {
            "success": true,
            "query": "Who is Anil?",
            "normalized_query": "anil",
            "results": {
                "people": [...],
                "places": [...],
                "memories": [...]
            },
            "response": "Anil Sharma is your son. He lives in Delhi, works in IT."
        }
    """
    
    try:
        # ============================================================
        # STEP 1: AUTHENTICATE
        # ============================================================
        user_id, auth_error = check_user_authenticated()
        if auth_error:
            return auth_error[0], auth_error[1]
        
        # ============================================================
        # STEP 2: VALIDATE REQUEST
        # ============================================================
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        
        if not query:
            return {"error": "Query is required"}, 400
        
        if len(query) > 500:
            return {"error": "Query is too long (max 500 characters)"}, 400
        
        # ============================================================
        # STEP 3: NORMALIZE QUERY
        # ============================================================
        normalized_query = normalize_query(query)
        
        if not normalized_query:
            # Empty after normalization (e.g., only punctuation)
            return {
                "success": False,
                "query": query,
                "normalized_query": normalized_query,
                "results": {"people": [], "places": [], "memories": []},
                "response": "I didn't understand that. Please try asking about a specific person, place, or memory."
            }, 200
        
        # ============================================================
        # STEP 4: SEARCH PATIENT'S MEMORY
        # ============================================================
        search_results = search_patient_memory(user_id, normalized_query)
        
        # ============================================================
        # STEP 5: GENERATE RESPONSE
        # ============================================================
        response_text = generate_response(query, search_results)
        
        # ============================================================
        # STEP 6: RETURN RESULT
        # ============================================================
        return {
            "success": True,
            "query": query,
            "normalized_query": normalized_query,
            "results": search_results,
            "response": response_text
        }, 200
        
    except Exception as e:
        print(f"Error in search_memory: {e}")
        return {
            "success": False,
            "error": "An error occurred during search. Please try again.",
            "response": "I had trouble searching your memory. Please try again later."
        }, 500
