import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parent.parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.product_model_verification import (
    NormalizeProductModel,
    VerifyProductModel,
)

TestCases = [
    (
        "Nike Sportswear Tech Fleece Joggers - Black",
        "NIKE TECH FLEECE JOGGER BLACK L",
        "Nike",
        "Nike",
        "SAME_MODEL",
        "Singular/plural jogger normalization",
    ),
    (
        "Champion Reverse Weave Crew - Grey",
        "CHAMPION REVERSE WEAVE CREWNECK GREY L",
        "Champion",
        "Champion",
        "SAME_MODEL",
        "Crew/crewneck normalization",
    ),
    (
        "Nike Air Force 1 '07 - White",
        "Nike Air Jordan 1 Retro Bred",
        "Nike",
        "Nike",
        "DIFFERENT_MODEL",
        "Shared number must not create a same-model result",
    ),
    (
        "Ralph Lauren Oxford Shirt",
        "Ralph Lauren Polo Shirt",
        "Ralph Lauren",
        "Ralph Lauren",
        "DIFFERENT_MODEL",
        "Generic shirt token must not create a same-model result",
    ),
    (
        "Nike Air Max 90 - White/Black",
        "NIKE AIRMAX 90 WHT BLK",
        "Nike",
        "Nike",
        "SAME_MODEL",
        "Existing verified alias case",
    ),
    (
        "Nike Air Force 1 '07 - White",
        "Nike AirForce 1 07 White",
        "Nike",
        "Nike",
        "SAME_MODEL",
        "Existing verified alias case",
    ),
    (
        "Adidas Ultraboost 22",
        "Adidas NMD R1",
        "Adidas",
        "Adidas",
        "DIFFERENT_MODEL",
        "Different Adidas model identifiers",
    ),
    (
        "ASICS Gel-Kayano 30",
        "ASICS Gel-Nimbus 25",
        "ASICS",
        "ASICS",
        "DIFFERENT_MODEL",
        "Different ASICS model identifiers",
    ),
]

print("=" * 72)
print("V4.2 PRODUCT MODEL REGRESSION TESTS")
print("=" * 72)

Failed = []

for Left, Right, LeftBrand, RightBrand, Expected, Description in TestCases:
    Actual, LeftKey, RightKey = VerifyProductModel(
        Left, Right, LeftBrand, RightBrand
    )
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
