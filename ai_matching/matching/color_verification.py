import re
from typing import Optional, Tuple

COLOR_ALIASES = {
    "core black": "black",
    "cloud white": "white",
    "optical white": "white",
    "all white": "white",
    "navy blue": "navy",
    "varsity red": "red",
}

COLOR_TOKENS = {
    "black", "white", "red", "blue", "green", "grey", "gray",
    "pink", "purple", "yellow", "orange", "brown", "beige",
    "cream", "tan", "silver", "gold", "navy", "charcoal",
    "olive", "khaki", "burgundy", "maroon", "teal",
}

def _clean(value: Optional[str]) -> str:
    if value is None:
        return ""
    value = str(value).strip().lower()
    if value in {"", "nan", "none", "null", "n/a", "na"}:
        return ""
    value = value.replace("&", " ")
    value = re.sub(r"[/,_-]+", " ", value)
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value

def _alias(value: str) -> str:
    # TNF is a brand prefix, not part of the color value.
    value = re.sub(r"^tnf\s+", "", value)
    for source in sorted(COLOR_ALIASES, key=len, reverse=True):
        value = re.sub(rf"\b{re.escape(source)}\b", COLOR_ALIASES[source], value)
    return re.sub(r"\s+", " ", value).strip()

def _parts(value: str) -> Tuple[set, set]:
    tokens = set(value.split())
    return tokens & COLOR_TOKENS, tokens - COLOR_TOKENS

def normalize_color(value: Optional[str]) -> str:
    cleaned = _clean(value)
    return _alias(cleaned) if cleaned else ""

def verify_color(stylehaus_color: Optional[str],
                 urbanthread_color: Optional[str]) -> Tuple[str, str, str]:
    """
    Returns (classification, normalized_stylehaus, normalized_urbanthread).

    EXACT_MATCH: cleaned source strings are identical.
    NORMALIZED_MATCH: approved aliases match, or complete color components
                      match despite order differences.
    MISMATCH: complete color component sets differ, including partial overlap.
    UNKNOWN: missing values, or same base colors with unresolved descriptors.
    """
    left_raw = _clean(stylehaus_color)
    right_raw = _clean(urbanthread_color)

    if not left_raw or not right_raw:
        return "UNKNOWN", normalize_color(stylehaus_color), normalize_color(urbanthread_color)

    left = _alias(left_raw)
    right = _alias(right_raw)

    if left_raw == right_raw:
        return "EXACT_MATCH", left, right

    left_colors, left_descriptors = _parts(left)
    right_colors, right_descriptors = _parts(right)

    if left_colors and right_colors and left_colors != right_colors:
        return "MISMATCH", left, right

    if left_colors and right_colors and left_colors == right_colors:
        if left_descriptors != right_descriptors:
            return "UNKNOWN", left, right
        return "NORMALIZED_MATCH", " ".join(sorted(left_colors)), " ".join(sorted(right_colors))

    return "UNKNOWN", left, right
