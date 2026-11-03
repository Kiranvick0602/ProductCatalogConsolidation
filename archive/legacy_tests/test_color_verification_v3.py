import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parent.parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.color_verification import verify_color

CASES = [
    ("Exact black", "Black", "Black", "EXACT_MATCH"),
    ("Approved brand alias", "Core Black", "Black", "NORMALIZED_MATCH"),
    ("White alias", "Optical White", "White", "NORMALIZED_MATCH"),
    ("Composite order variation", "Black/Red", "Red/Black", "NORMALIZED_MATCH"),
    ("Clearly different colors", "Flamingo Pink", "Green", "MISMATCH"),
    ("Different base colors", "Thunder Blue", "Black/Red", "MISMATCH"),
    ("Different colors with composite", "Core Black", "White/Green", "MISMATCH"),
    ("Different color families", "Charcoal", "Navy", "MISMATCH"),
    ("Shade descriptor", "Spruce Green", "Green", "UNKNOWN"),
    ("Finish descriptor", "Black Smooth", "Black", "UNKNOWN"),
    ("Material descriptor", "Wheat Nubuck", "Wheat", "UNKNOWN"),
    ("Wash descriptor", "Stonewash Grey", "Grey", "UNKNOWN"),
    ("Oxford shade descriptor", "Oxford Grey", "Grey", "UNKNOWN"),
    ("Partial composite overlap", "White/Green", "Green", "UNKNOWN"),
    ("Missing left color", None, "Black", "UNKNOWN"),
    ("Both missing", None, None, "UNKNOWN"),
]

failed = 0
print("=" * 72)
print("COLOR VERIFICATION V3 REGRESSION TESTS")
print("=" * 72)
for name, left, right, expected in CASES:
    actual, left_norm, right_norm = verify_color(left, right)
    passed = actual == expected
    print(f"{'PASS' if passed else 'FAIL'}: {name}")
    print(f"  Expected: {expected} | Actual: {actual}")
    print(f"  Normalized: '{left_norm}' <> '{right_norm}'")
    if not passed:
        failed += 1

print()
print(f"Total tests: {len(CASES)}")
print(f"Passed: {len(CASES) - failed}")
print(f"Failed: {failed}")
if failed:
    raise SystemExit(1)
print("All color verification regression tests passed.")
