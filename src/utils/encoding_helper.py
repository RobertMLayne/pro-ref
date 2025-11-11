
from urllib.parse import quote

COMMON_ENCODINGS = {
    ' ': '%20',
    '"': '%22',
    '#': '%23',
    '%': '%25',
    '<': '%3C',
    '>': '%3E',
    '|': '%7C',
}

def encode_query_part(s: str) -> str:
    return quote(s, safe=':(),[]')  # keep DSL tokens visible

def suggest_encoding_issue(url: str) -> str:
    suggestions = []
    for ch, enc in COMMON_ENCODINGS.items():
        if ch in url:
            suggestions.append(f"Replace '{ch}' with '{enc}'")
    return "; ".join(suggestions) if suggestions else "No obvious URL-encoding issues detected."
