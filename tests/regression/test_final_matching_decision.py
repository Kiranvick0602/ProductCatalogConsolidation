import sys
from pathlib import Path
import pandas as pd
import pytest

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.final_decision import decide_row


def row(**kwargs):
    base = {
        "VerifiedBrandMatch": "EXACT_MATCH",
        "VerifiedProductModelMatch_V4_3_1": "SAME_MODEL",
        "VerifiedColorMatch_V3_1": "EXACT_MATCH",
        "VerifiedSizeMatch": "EXACT_MATCH",
        "StyleHaus_Size": "M",
        "UrbanThread_Size": "M"
    }
    base.update(kwargs)
    return pd.Series(base)


cases = [
    ("All verified", row(), "MATCH"),
    ("Different model", row(VerifiedProductModelMatch_V4_3_1="DIFFERENT_MODEL"), "NO_MATCH"),
    ("Color mismatch", row(VerifiedColorMatch_V3_1="MISMATCH"), "NO_MATCH"),
    ("Size mismatch", row(VerifiedSizeMatch="MISMATCH"), "NO_MATCH"),
    ("Unknown model", row(VerifiedProductModelMatch_V4_3_1="UNKNOWN"), "REVIEW"),
    ("Unknown color", row(VerifiedColorMatch_V3_1="UNKNOWN"), "REVIEW"),
    ("Unknown size", row(VerifiedSizeMatch="UNKNOWN", StyleHaus_Size="", UrbanThread_Size=""), "REVIEW"),
    ("Explicit M vs L for same model", row(VerifiedSizeMatch="UNKNOWN", StyleHaus_Size="M", UrbanThread_Size="L"), "NO_MATCH"),
    ("Mismatch overrides unknown", row(VerifiedColorMatch_V3_1="MISMATCH", VerifiedProductModelMatch_V4_3_1="UNKNOWN"), "NO_MATCH"),
]


@pytest.mark.regression
@pytest.mark.parametrize("name,data,expected", cases)
def test_final_matching_decision_case(name, data, expected):
    actual = decide_row(data)["FinalMatchDecision"]
    assert actual == expected, f"Case '{name}' failed: expected {expected}, got {actual}"


def run_standalone():
    failed = 0
    for name, data, expected in cases:
        actual = decide_row(data)["FinalMatchDecision"]
        print(f"{'PASS' if actual == expected else 'FAIL'}: {name} | expected={expected}, actual={actual}")
        failed += (actual != expected)
    print(f"\nTotal: {len(cases)} | Passed: {len(cases)-failed} | Failed: {failed}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run_standalone()
