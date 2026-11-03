import re
import pandas as pd

def _norm_size(value):
    if pd.isna(value):
        return ""
    value = str(value).strip().lower()
    value = re.sub(r"^us\s+", "", value)
    value = re.sub(r"\s+", "", value)
    return value

def resolve_size_result(row):
    """
    Use existing size verification first.
    For SAME_MODEL rows only, resolve explicit size differences when the
    existing verifier returned UNKNOWN and both raw size labels are present.
    """
    result = str(row.get("VerifiedSizeMatch", "")).strip().upper()
    if result in {"EXACT_MATCH", "NORMALIZED_MATCH", "MISMATCH"}:
        return result

    left = _norm_size(row.get("StyleHaus_Size"))
    right = _norm_size(row.get("UrbanThread_Size"))
    if not left or not right:
        return "UNKNOWN"

    model = str(row.get("VerifiedProductModelMatch_V4_3_1", "")).strip().upper()
    if model != "SAME_MODEL":
        return "UNKNOWN"

    # Do not infer conversions between unlike size systems. For direct
    # labels such as M/L, S/M, numeric shoe sizes, and waist/inseam sizes,
    # a clear unequal value is a mismatch.
    if left != right:
        return "MISMATCH"
    return "UNKNOWN"

def decide_row(row):
    brand = str(row.get("VerifiedBrandMatch", "UNKNOWN")).upper()
    model = str(row.get("VerifiedProductModelMatch_V4_3_1", "UNKNOWN")).upper()
    color = str(row.get("VerifiedColorMatch_V3_1", "UNKNOWN")).upper()
    size = resolve_size_result(row)

    # Evaluate confirmed hard mismatches first. This prevents an UNKNOWN
    # in another attribute from hiding a definite mismatch.
    mismatches = []
    if brand == "MISMATCH":
        mismatches.append("Brand mismatch")
    if model == "DIFFERENT_MODEL":
        mismatches.append("Different product models")
    if color == "MISMATCH":
        mismatches.append("Color mismatch")
    if size == "MISMATCH":
        mismatches.append("Size mismatch")

    if mismatches:
        return pd.Series({
            "FinalMatchDecision": "NO_MATCH",
            "DecisionReason": "; ".join(mismatches),
            "FinalVerifiedSizeMatch": size
        })

    unknowns = []
    if brand not in {"EXACT_MATCH", "NORMALIZED_MATCH"}:
        unknowns.append("Brand verification unresolved")
    if model != "SAME_MODEL":
        unknowns.append("Product model verification unresolved")
    if color not in {"EXACT_MATCH", "NORMALIZED_MATCH"}:
        unknowns.append("Color verification unresolved")
    if size not in {"EXACT_MATCH", "NORMALIZED_MATCH"}:
        unknowns.append("Size verification unresolved")

    if unknowns:
        return pd.Series({
            "FinalMatchDecision": "REVIEW",
            "DecisionReason": "; ".join(unknowns),
            "FinalVerifiedSizeMatch": size
        })

    return pd.Series({
        "FinalMatchDecision": "MATCH",
        "DecisionReason": "Brand, product model, color, and size verified",
        "FinalVerifiedSizeMatch": size
    })
