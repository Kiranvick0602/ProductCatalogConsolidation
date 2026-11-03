import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

OutputFolder = Path("data/output")

InputFile = (
    OutputFolder /
    "CandidatePairs_ProductModelVerification_V3.csv"
)

AuditFolder = (
    OutputFolder /
    "quality" /
    "product_model_audit"
)

AuditFolder.mkdir(parents=True, exist_ok=True)


# ============================================================
# READ DATA
# ============================================================

CandidateDf = pd.read_csv(
    InputFile,
    dtype=str,
    keep_default_na=False
)


# ============================================================
# FILTER DIFFERENT MODEL RECORDS
# ============================================================

DifferentModelDf = CandidateDf[
    CandidateDf["VerifiedProductModelMatch"] == "DIFFERENT_MODEL"
].copy()


# ============================================================
# SELECT AUDIT COLUMNS
# ============================================================

AuditColumns = [
    "CandidatePairID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "StyleHaus_Brand",
    "UrbanThread_Brand",
    "StyleHaus_NormalizedProductModel",
    "UrbanThread_NormalizedProductModel",
    "VerifiedProductModelMatch"
]

AuditDf = DifferentModelDf[AuditColumns].copy()


# ============================================================
# EXPORT
# ============================================================

OutputFile = (
    AuditFolder /
    "Different_Product_Models_Audit_V3.csv"
)

AuditDf.to_csv(
    OutputFile,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("=" * 65)
print("DIFFERENT PRODUCT MODEL AUDIT V3")
print("=" * 65)

print(f"Total candidate pairs: {len(CandidateDf)}")

print(f"Different model records: {len(AuditDf)}")

print(f"Unique CandidatePairIDs: {AuditDf['CandidatePairID'].nunique()}")

print(f"\nSaved: {OutputFile.resolve()}")

print("\nAudit completed successfully.")