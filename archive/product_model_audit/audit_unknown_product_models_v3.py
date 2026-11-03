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
# READ INPUT
# ============================================================

CandidateDf = pd.read_csv(
    InputFile,
    dtype=str,
    keep_default_na=False
)

# ============================================================
# FILTER UNKNOWN PRODUCT MODELS
# ============================================================

UnknownModelDf = CandidateDf[
    CandidateDf["VerifiedProductModelMatch"] == "UNKNOWN"
].copy()

# ============================================================
# SELECT AUDIT COLUMNS
# ============================================================

PreferredColumns = [
    "CandidatePairID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "StyleHaus_Brand",
    "UrbanThread_Brand",
    "StyleHaus_NormalizedProductModel",
    "UrbanThread_NormalizedProductModel",
    "VerifiedProductModelMatch",
    "CosineSimilarity",
    "VerifiedProductNameMatch",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

AuditColumns = [
    Column
    for Column in PreferredColumns
    if Column in UnknownModelDf.columns
]

AuditDf = UnknownModelDf[AuditColumns].copy()

# ============================================================
# SAVE AUDIT FILE
# ============================================================

OutputFile = (
    AuditFolder /
    "Unknown_Product_Models_Audit_V3.csv"
)

AuditDf.to_csv(OutputFile, index=False)

# ============================================================
# SUMMARY
# ============================================================

print("=" * 65)
print("UNKNOWN PRODUCT MODEL AUDIT V3")
print("=" * 65)

print(f"Total candidate pairs: {len(CandidateDf)}")
print(f"Unknown model records: {len(UnknownModelDf)}")
print(
    f"Unique CandidatePairIDs: "
    f"{UnknownModelDf['CandidatePairID'].nunique()}"
)

print("\nAudit columns:")
for Column in AuditColumns:
    print(f"- {Column}")

print(f"\nSaved: {OutputFile.resolve()}")

print("\nAudit completed successfully.")