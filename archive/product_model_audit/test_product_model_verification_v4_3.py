import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parent.parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.product_model_verification import VerifyProductModel

TestCases = [
    ("New Balance 990v6 - Grey", "New Balance 990v6 Grey Made in USA", "New Balance", "New Balance", "SAME_MODEL", "Made in USA descriptor"),
    ("Ralph Lauren Classic Fit Polo - Navy", "Polo Ralph Lauren Cable Knit Sweater Navy", "Ralph Lauren", "Ralph Lauren", "DIFFERENT_MODEL", "Polo vs cable-knit sweater"),
    ("Ralph Lauren Classic Fit Polo - Navy", "Ralph Lauren Polo Shirt Navy", "Ralph Lauren", "Ralph Lauren", "SAME_MODEL", "Polo naming variation"),
    ("The North Face 1996 Retro Nuptse - Black", "The North Face Nuptse 1996 Black", "The North Face", "The North Face", "SAME_MODEL", "Nuptse model token order"),
    ("The North Face 1996 Retro Nuptse - Red", "The North Face Nuptse 1996 Black", "The North Face", "The North Face", "SAME_MODEL", "Same model, different color"),
    ("Patagonia Better Sweater - Grey", "Patagonia Better Sweater Fleece Grey", "Patagonia", "Patagonia", "SAME_MODEL", "Better Sweater descriptor"),
    ("Carhartt WIP Chase V-Neck Tee - Green", "Carhartt WIP Chase Hoodie Grey", "Carhartt", "Carhartt", "DIFFERENT_MODEL", "Tee vs hoodie"),
    ("Converse Chuck Taylor All Star - White", "Converse Run Star Hike Platform Black", "Converse", "Converse", "DIFFERENT_MODEL", "Chuck Taylor vs Run Star"),
    ("Converse Chuck Taylor All Star - White", "Converse Chuck Taylor Hi White", "Converse", "Converse", "UNKNOWN", "Explicitly unresolved Converse case"),
    ("Dr. Martens 1460 Boot - Black", "Dr. Martens 1460 8 Eye Boot Black", "Dr. Martens", "Dr. Martens", "SAME_MODEL", "8 Eye descriptor"),
    ("Birkenstock Arizona - Brown", "Birkenstock Arizona Habana Brown 42", "Birkenstock", "Birkenstock", "SAME_MODEL", "Arizona EU size"),
    ("Air Jordan 1 Retro High OG - Red/Black", "Nike Air Jordan 1 Retro Bred", "Nike", "Nike", "UNKNOWN", "Explicitly unresolved Air Jordan colorway"),
    ("UGG Classic Short II - Chestnut (W)", "UGG Classic Short Chestnut W7", "UGG", "UGG", "SAME_MODEL", "Classic Short II alias"),
    ("Dickies 874 Original Fit Work Pant - Black", "Dickies 874 Work Pant Black 32", "Dickies", "Dickies", "SAME_MODEL", "Waist size"),
    ("Barbour Bedale Wax Jacket - Olive", "Barbour Ashby Wax Jacket Olive", "Barbour", "Barbour", "DIFFERENT_MODEL", "Bedale vs Ashby"),
]

print("=" * 72)
print("V4.3 PRODUCT MODEL REGRESSION TESTS")
print("=" * 72)

Failed = []
for Left, Right, LeftBrand, RightBrand, Expected, Description in TestCases:
    Actual, LeftKey, RightKey = VerifyProductModel(Left, Right, LeftBrand, RightBrand)
    Status = "PASS" if Actual == Expected else "FAIL"
    print(f"{Status}: {Description}")
    print(f"  Expected: {Expected} | Actual: {Actual}")
    print(f"  Keys: '{LeftKey}' <> '{RightKey}'")
    if Actual != Expected:
        Failed.append((Description, Expected, Actual))

print(f"\nTotal tests: {len(TestCases)}")
print(f"Passed: {len(TestCases) - len(Failed)}")
print(f"Failed: {len(Failed)}")
if Failed:
    raise SystemExit("Regression tests failed.")
print("\nAll regression tests passed.")
