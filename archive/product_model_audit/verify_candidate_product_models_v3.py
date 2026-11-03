import sys
import pandas as pd
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ProjectRoot))

print(f"Project Root: {ProjectRoot}")
print(f"Python Path: {sys.path[0]}")


from ai_matching.matching.product_model_verification import (
    NormalizeProductModel,
    VerifyProductModel
)

# ============================================================
# CONFIGURATION
# ============================================================

OutputFolder = Path("data/output")

InputFile = OutputFolder / "CandidatePairs_MaterialVerification_V2.csv"
OutputFile = OutputFolder / "CandidatePairs_ProductModelVerification_V3.csv"

if not InputFile.exists():
    raise FileNotFoundError(f"Input file not found: {InputFile.resolve()}")

CandidateDf = pd.read_csv(
    InputFile,
    dtype=str,
    keep_default_na=False
)

RequiredColumns = [
    "CandidatePairID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "StyleHaus_Brand",
    "UrbanThread_Brand"
]

MissingColumns = [
    column for column in RequiredColumns
    if column not in CandidateDf.columns
]

if MissingColumns:
    raise ValueError(f"Missing required columns: {MissingColumns}")

if CandidateDf["CandidatePairID"].duplicated().any():
    raise ValueError("CandidatePairID contains duplicates.")

# ============================================================
# NORMALIZED MODEL KEYS
# ============================================================

CandidateDf["StyleHaus_NormalizedProductModel"] = CandidateDf.apply(
    lambda row: NormalizeProductModel(
        row["StyleHaus_ProductName"],
        row["StyleHaus_Brand"]
    ),
    axis=1
)

CandidateDf["UrbanThread_NormalizedProductModel"] = CandidateDf.apply(
    lambda row: NormalizeProductModel(
        row["UrbanThread_ProductName"],
        row["UrbanThread_Brand"]
    ),
    axis=1
)

# ============================================================
# PRODUCT MODEL VERIFICATION
# ============================================================

CandidateDf["VerifiedProductModelMatch"] = CandidateDf.apply(
    lambda row: VerifyProductModel(
        row["StyleHaus_ProductName"],
        row["UrbanThread_ProductName"],
        row["StyleHaus_Brand"],
        row["UrbanThread_Brand"]
    ),
    axis=1
)

# ============================================================
# SUMMARY
# ============================================================

print("=" * 65)
print("PRODUCT MODEL VERIFICATION V3")
print("=" * 65)

print(
    CandidateDf["VerifiedProductModelMatch"]
    .value_counts(dropna=False)
    .to_string()
)

print(f"\nTotal candidate pairs: {len(CandidateDf)}")
print(f"Unique CandidatePairIDs: {CandidateDf['CandidatePairID'].nunique()}")

# ============================================================
# VALIDATE REQUIRED EXAMPLES
# ============================================================

TestCases = [
    (
        "Nike Air Max 90 - White/Black",
        "NIKE AIRMAX 90 WHT BLK",
        "Nike",
        "Nike",
        "SAME_MODEL"
    ),
    (
        "Nike Air Force 1 '07 - White",
        "Nike AirForce 1 07 White",
        "Nike",
        "Nike",
        "SAME_MODEL"
    ),
    (
        "Adidas Ultraboost 22",
        "Adidas NMD R1",
        "Adidas",
        "Adidas",
        "DIFFERENT_MODEL"
    ),
    (
        "ASICS Gel-Kayano 30",
        "ASICS Gel-Nimbus 25",
        "ASICS",
        "ASICS",
        "DIFFERENT_MODEL"
    )
]

print("\nEXAMPLE VALIDATION")
print("-" * 65)

for left_name, right_name, left_brand, right_brand, expected in TestCases:
    actual = VerifyProductModel(
        left_name,
        right_name,
        left_brand,
        right_brand
    )

    status = "PASS" if actual == expected else "CHECK"

    print(f"{status}: {left_name} <-> {right_name}")
    print(f"       Expected={expected}, Actual={actual}")

# ============================================================
# EXPORT
# ============================================================

CandidateDf.to_csv(OutputFile, index=False)

print(f"\nSaved: {OutputFile.resolve()}")
print("Product model verification completed.")
