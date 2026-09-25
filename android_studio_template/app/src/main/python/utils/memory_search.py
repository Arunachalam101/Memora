"""
MEMORA Memory Search Utility - Phase 10C
Handles searching patient's memory records across People, Places, and Memories
"""

from models.models import MemoryPerson, MemoryPlace, MemoryItem
from sqlalchemy import or_


def normalize_query(query):
    """
    Normalize query: lowercase, strip punctuation, remove whitespace.
    Support variations like: "Who is Anil?", "who's anil", "tell me about anil"
    
    Args:
        query: user's original query string
        
    Returns:
        normalized_query: str (lowercased, no punctuation)
    """
    import re
    
    query = query.lower().strip()
    
    # Remove common question prefixes
    prefixes = ["who is", "who's", "who am i", "where is", "tell me about", 
                "describe", "how is", "what about"]
    for prefix in prefixes:
        if query.startswith(prefix):
            query = query[len(prefix):].strip()
            break
    
    # Remove punctuation
    query = re.sub(r'[?!.,;:\"\']', '', query)
    
    return query.strip()


def search_patient_memory(user_id, query):
    """
    Search patient's memory records across all types.
    Searches multiple fields per type using case-insensitive LIKE queries.
    
    Args:
        user_id: authenticated user ID (from session)
        query: search query string
        
    Returns:
        results: dict with 'people', 'places', 'memories' lists
    """
    
    results = {
        'people': [],
        'places': [],
        'memories': []
    }
    
    # Validate inputs
    if not user_id or not query:
        return results
    
    query_pattern = f"%{query}%"
    
    # ============================================================
    # SEARCH PEOPLE: name, relationship, description
    # ============================================================
    try:
        people = MemoryPerson.query.filter_by(
            patient_id=user_id,
            is_active=True
        ).filter(
            or_(
                MemoryPerson.name.ilike(query_pattern),
                MemoryPerson.relationship.ilike(query_pattern),
                MemoryPerson.description.ilike(query_pattern)
            )
        ).all()
        results['people'] = [p.to_dict() for p in people]
    except Exception as e:
        print(f"Error searching people: {e}")
    
    # ============================================================
    # SEARCH PLACES: name, description
    # ============================================================
    try:
        places = MemoryPlace.query.filter_by(
            patient_id=user_id,
            is_active=True
        ).filter(
            or_(
                MemoryPlace.name.ilike(query_pattern),
                MemoryPlace.description.ilike(query_pattern)
            )
        ).all()
        results['places'] = [pl.to_dict() for pl in places]
    except Exception as e:
        print(f"Error searching places: {e}")
    
    # ============================================================
    # SEARCH MEMORIES: title, description
    # ============================================================
    try:
        memories = MemoryItem.query.filter_by(
            patient_id=user_id,
            is_active=True
        ).filter(
            or_(
                MemoryItem.title.ilike(query_pattern),
                MemoryItem.description.ilike(query_pattern)
            )
        ).all()
        results['memories'] = [m.to_dict() for m in memories]
    except Exception as e:
        print(f"Error searching memories: {e}")
    
    return results
