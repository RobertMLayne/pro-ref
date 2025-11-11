
import urllib.parse

def suggest_url_encoding(query: str) -> list[str]:
    """
    Given a raw q string intended for GET, suggest encodings for common characters.
    """
    suggestions = []
    mapping = {' ': '%20', '"': '%22', '#': '%23', '%': '%25', '<': '%3C', '>': '%3E', '|': '%7C'}
    for ch, enc in mapping.items():
        if ch in query and enc not in query:
            suggestions.append(f"Replace '{ch}' with '{enc}'")
    suggestions.append("Full encoding: " + urllib.parse.quote(query, safe=':()*[]'))
    return suggestions
