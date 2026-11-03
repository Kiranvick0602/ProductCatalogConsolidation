import re
import unicodedata
from typing import Optional, Set, Tuple

# V4.3 builds on V4.2 with narrowly scoped, audit-driven normalization.
# SAME_MODEL requires equality of normalized model keys.
# Ambiguous product-family cases are intentionally kept UNKNOWN.

ALIASES = {
    "airmax": "air max",
    "airforce": "air force",
    "gelkayano": "gel kayano",
    "gelnimbus": "gel nimbus",
    "vapormax": "vapor max",
    "wht": "white",
    "blk": "black",
    "blu": "blue",
    "grn": "green",
    "gry": "gray",
    "grey": "gray",
    "jkt": "jacket",
    "drmartens": "dr martens",
    "rayban": "ray ban",
    "levis": "levis",
    "joggers": "jogger",
    "crewneck": "crew",
}

COLOR_TOKENS = {
    "black", "white", "gray", "silver", "red", "blue", "navy", "green",
    "brown", "tan", "beige", "cream", "yellow", "pink", "purple", "orange",
    "gold", "wheat", "olive", "charcoal", "burgundy", "indigo", "chestnut",
    "khaki", "multi", "multicolor", "natural", "stone", "bone", "sail",
    "habana", "bred",
}

BRAND_TOKENS = {
    "nike", "adidas", "asics", "saucony", "hoka", "puma", "reebok", "vans",
    "converse", "birkenstock", "levi", "levis", "ray", "ban", "timberland",
    "ugg", "patagonia", "barbour", "carhartt", "champion", "salomon",
    "dr", "martens", "canada", "goose", "north", "face", "ralph", "lauren",
    "hugo", "boss", "brooks", "fjallraven", "new", "balance", "on",
}

DESCRIPTIVE_TOKENS = {
    "original", "classic", "premium", "retro", "new", "style", "sportswear",
    "womens", "women", "mens", "men", "unisex", "usa", "made", "fit",
    "slim", "regular", "relaxed", "oversized", "og", "xxi",
    "medium", "wash",
}

# Product types that should not be treated as the same model.
INCOMPATIBLE_TYPES = [
    {"hoodie", "sweatshirt", "tee", "tshirt"},
    {"jeans", "pant", "pants", "trouser", "trousers", "jogger"},
    {"jacket", "coat", "bomber"},
    {"boot", "boots", "clog", "clogs", "sandal", "sandals"},
    {"backpack", "bag"},
    {"polo", "oxford"},
    {"polo", "sweater"},
]

# Generic terms are excluded from overlap-based DIFFERENT_MODEL evidence.
# Chuck/Taylor/All/Star are deliberately retained because they identify
# Converse product lines (e.g. Chuck Taylor All Star vs Run Star Hike).
GENERIC_OVERLAP = {
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "shirt", "tee", "tshirt", "shoe", "shoes", "sneaker", "sneakers",
    "jacket", "coat", "pant", "pants", "jeans", "boot", "boots",
    "bag", "backpack", "polo", "hoodie", "sweatshirt", "sweater",
    "air", "max", "force", "gel", "fresh", "foam", "tech", "fleece",
    "reverse", "weave", "crew",
}

def _normalize_raw(value: Optional[str]) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[’']", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Remove the complete catalog phrase, not just individual words.
    text = re.sub(r"\bmade in usa\b", " ", text)

    # Reviewed equivalent model-name ordering.
    text = re.sub(r"\b1996(?:\s+retro)?\s+nuptse\b", "nuptse 1996", text)

    # UGG Classic Short II is treated as the same model naming variant as
    # UGG Classic Short for this matching task.
    text = re.sub(r"\bclassic short ii\b", "classic short", text)

    expanded = []
    for token in text.split():
        expanded.extend(ALIASES.get(token, token).split())
    return " ".join(expanded)

def _brand_set(brand: Optional[str]) -> Set[str]:
    return set(_normalize_raw(brand).split()) if brand else set()

def _remove_explicit_size_patterns(text: str) -> str:
    text = re.sub(r"\b(?:size|us|uk|eu)\s*\d{1,2}(?:\.\d)?\b", " ", text)
    text = re.sub(r"\bw\d{1,2}\b", " ", text)
    text = re.sub(r"\b(?:xs|s|m|l|xl|xxl|xxxl|w)\b", " ", text)

    # Remove numeric sizes only in known size-bearing contexts.
    # Remove a trailing EU shoe size from Arizona product names.
    if "arizona" in text:
        text = re.sub(r"\s+(?:36|37|38|39|40|41|42|43|44|45|46)\s*$", "", text)

    # Remove a trailing waist size when the product is clearly a pant/jean.
    if re.search(r"\b(?:pant|pants|jeans|trouser|trousers)\b", text):
        text = re.sub(r"\s+(?:28|29|30|31|32|33|34|35|36|38|40|42|44|46)\s*$", "", text)

    return re.sub(r"\s+", " ", text).strip()

def NormalizeProductModel(ProductName: Optional[str], Brand: Optional[str] = None) -> str:
    text = _remove_explicit_size_patterns(_normalize_raw(ProductName))
    brand_tokens = _brand_set(Brand) or BRAND_TOKENS

    # Targeted model-name phrase handling.
    text = re.sub(r"\b8 eye\b", " ", text)
    text = re.sub(r"\bbetter sweater fleece\b", "better sweater", text)
    text = re.sub(r"\bpolo shirt\b", "polo", text)
    text = re.sub(r"\bclassic short w\b", "classic short", text)

    result = []
    for token in text.split():
        if token in brand_tokens:
            continue
        if token in COLOR_TOKENS:
            continue
        if token in DESCRIPTIVE_TOKENS:
            continue
        result.append(token)

    return " ".join(result).strip()

def _has_incompatible_type(left: Set[str], right: Set[str]) -> bool:
    for group in INCOMPATIBLE_TYPES:
        left_types = left.intersection(group)
        right_types = right.intersection(group)
        if left_types and right_types and not left_types.intersection(right):
            return True
    return False

def _model_numbers(tokens: Set[str]) -> Set[str]:
    return {token for token in tokens if re.search(r"\d", token)}

def _substantive(tokens: Set[str]) -> Set[str]:
    return tokens - GENERIC_OVERLAP

def VerifyProductModel(
    StyleHausProductName: Optional[str],
    UrbanThreadProductName: Optional[str],
    StyleHausBrand: Optional[str] = None,
    UrbanThreadBrand: Optional[str] = None,
) -> Tuple[str, str, str]:
    LeftRaw = _normalize_raw(StyleHausProductName)
    RightRaw = _normalize_raw(UrbanThreadProductName)

    # "Polo" is also the Ralph Lauren sub-brand. Distinguish a polo garment
    # from a cable-knit sweater using the full product phrase.
    LeftIsPoloGarment = (
        "classic fit polo" in LeftRaw or "polo shirt" in LeftRaw
    )
    RightIsPoloGarment = (
        "classic fit polo" in RightRaw or "polo shirt" in RightRaw
    )
    LeftIsCableKnitSweater = "cable knit sweater" in LeftRaw
    RightIsCableKnitSweater = "cable knit sweater" in RightRaw
    if (
        (LeftIsPoloGarment and RightIsCableKnitSweater)
        or (RightIsPoloGarment and LeftIsCableKnitSweater)
    ):
        LeftKey = NormalizeProductModel(StyleHausProductName, StyleHausBrand)
        RightKey = NormalizeProductModel(UrbanThreadProductName, UrbanThreadBrand)
        return "DIFFERENT_MODEL", LeftKey, RightKey

    # Preserve the two explicitly unresolved cases from the audit.
    BothConverseChuckTaylor = (
        "chuck taylor all star" in LeftRaw and "chuck taylor hi" in RightRaw
    ) or (
        "chuck taylor hi" in LeftRaw and "chuck taylor all star" in RightRaw
    )
    if BothConverseChuckTaylor:
        LeftKey = NormalizeProductModel(StyleHausProductName, StyleHausBrand)
        RightKey = NormalizeProductModel(UrbanThreadProductName, UrbanThreadBrand)
        return "UNKNOWN", LeftKey, RightKey

    # Chuck Taylor and Run Star are distinct Converse product lines.
    IsChuckTaylorVsRunStar = (
        ("chuck taylor" in LeftRaw and "run star" in RightRaw)
        or ("run star" in LeftRaw and "chuck taylor" in RightRaw)
    )
    if IsChuckTaylorVsRunStar:
        LeftKey = NormalizeProductModel(StyleHausProductName, StyleHausBrand)
        RightKey = NormalizeProductModel(UrbanThreadProductName, UrbanThreadBrand)
        return "DIFFERENT_MODEL", LeftKey, RightKey

    # Air Jordan 1 Retro High OG vs Air Jordan 1 Retro Bred remains UNKNOWN.
    IsAirJordanHighOgVsBred = (
        "air jordan 1" in LeftRaw and "high og" in LeftRaw and "bred" in RightRaw
    ) or (
        "air jordan 1" in RightRaw and "high og" in RightRaw and "bred" in LeftRaw
    )
    if IsAirJordanHighOgVsBred:
        LeftKey = NormalizeProductModel(StyleHausProductName, StyleHausBrand)
        RightKey = NormalizeProductModel(UrbanThreadProductName, UrbanThreadBrand)
        return "UNKNOWN", LeftKey, RightKey

    LeftKey = NormalizeProductModel(StyleHausProductName, StyleHausBrand)
    RightKey = NormalizeProductModel(UrbanThreadProductName, UrbanThreadBrand)

    if not LeftKey or not RightKey:
        return "UNKNOWN", LeftKey, RightKey

    if LeftKey == RightKey:
        return "SAME_MODEL", LeftKey, RightKey

    LeftTokens = set(LeftKey.split())
    RightTokens = set(RightKey.split())

    # Explicitly audited Barbour model distinction.
    if (
        ("bedale" in LeftTokens and "ashby" in RightTokens)
        or ("ashby" in LeftTokens and "bedale" in RightTokens)
    ):
        return "DIFFERENT_MODEL", LeftKey, RightKey

    if _has_incompatible_type(LeftTokens, RightTokens):
        return "DIFFERENT_MODEL", LeftKey, RightKey

    LeftNumbers = _model_numbers(LeftTokens)
    RightNumbers = _model_numbers(RightTokens)
    SharedSubstantive = _substantive(LeftTokens).intersection(_substantive(RightTokens))

    if LeftNumbers and RightNumbers and LeftNumbers.isdisjoint(RightNumbers):
        if SharedSubstantive or LeftTokens.intersection(RightTokens):
            return "DIFFERENT_MODEL", LeftKey, RightKey

    LeftSubstantive = _substantive(LeftTokens)
    RightSubstantive = _substantive(RightTokens)

    if LeftSubstantive and RightSubstantive and not SharedSubstantive:
        return "DIFFERENT_MODEL", LeftKey, RightKey

    return "UNKNOWN", LeftKey, RightKey
