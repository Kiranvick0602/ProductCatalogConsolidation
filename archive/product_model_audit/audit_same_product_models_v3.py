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
# FILTER SAME MODEL RECORDS
# ============================================================

SameModelDf = CandidateDf[
    CandidateDf["VerifiedProductModelMatch"] == "SAME_MODEL"
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
    "VerifiedProductNameMatch",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

AuditColumns = [
    Column
    for Column in PreferredColumns
    if Column in SameModelDf.columns
]

AuditDf = SameModelDf[AuditColumns].copy()

# ============================================================
# SAVE AUDIT FILE
# ============================================================

OutputFile = (
    AuditFolder /
    "Same_Product_Models_Audit_V3.csv"
)

AuditDf.to_csv(OutputFile, index=False)

# ============================================================
# SUMMARY
# ============================================================

print("=" * 65)
print("SAME PRODUCT MODEL AUDIT V3")
print("=" * 65)

print(f"Total candidate pairs: {len(CandidateDf)}")
print(f"Same model records: {len(SameModelDf)}")
print(
    f"Unique CandidatePairIDs: "
    f"{SameModelDf['CandidatePairID'].nunique()}"
)

print("\nSaved:", OutputFile.resolve())
print("\nAudit completed successfully.")
