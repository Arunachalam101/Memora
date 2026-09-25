"""
MEMORA Response Generation Utility - Phase 10C
Generates deterministic, template-based responses from search results.
NO LLM, NO AI provider, NO external API calls.
"""


def generate_response(query, results):
    """
    Generate response from search results.
    Deterministic templates only, no ML/AI/LLM.
    
    Args:
        query: original query string (for logging/debugging)
        results: dict with 'people', 'places', 'memories' lists
        
    Returns:
        response_text: str (always a response, never None)
    """
    
    # Case 1: No matches found
    if not any(results.values()):
        return "I don't have that information saved yet. You can ask your caregiver to add it to your Memory Album."
    
    # Case 2: Match found - Prioritize: people > places > memories
    
    # PEOPLE match
    if results['people']:
        person = results['people'][0]  # First match only
        name = person.get('name', 'Someone')
        relationship = person.get('relationship', 'a person')
        desc = person.get('description', '').strip()
        
        if desc:
            return f"{name} is your {relationship}. {desc}"
        else:
            return f"{name} is your {relationship}."
    
    # PLACES match
    if results['places']:
        place = results['places'][0]
        name = place.get('name', 'A place')
        desc = place.get('description', '').strip()
        
        if desc:
            return f"{name} is one of your saved places. {desc}"
        else:
            return f"{name} is one of your saved places."
    
    # MEMORIES match
    if results['memories']:
        memory = results['memories'][0]
        title = memory.get('title', 'Something')
        desc = memory.get('description', '').strip()
        
        if desc:
            return f"You have a memory about {title}. {desc}"
        else:
            return f"You have a memory about {title}."
    
    # Safety fallback (should not reach here)
    return "I'm not sure how to answer that. Please try asking about a person, place, or memory."
