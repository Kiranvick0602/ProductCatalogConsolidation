import pandas as pd
from pathlib import Path

OutputFolder = Path("data/output")

InputFile = (
    OutputFolder /
    "CandidatePairs_ProductModelVerification_V4_2.csv"
)

AuditFolder = (
    OutputFolder /
    "quality" /
    "product_model_audit"
)

AuditFolder.mkdir(parents=True, exist_ok=True)

CandidateDf = pd.read_csv(
    InputFile,
    dtype=str,
    keep_default_na=False
)

UnknownModelDf = CandidateDf[
    CandidateDf["VerifiedProductModelMatch_V4_2"] == "UNKNOWN"
].copy()

AuditColumns = [
    "CandidatePairID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "StyleHaus_Brand",
    "UrbanThread_Brand",
    "StyleHaus_NormalizedProductModel_V4_2",
    "UrbanThread_NormalizedProductModel_V4_2",
    "VerifiedProductModelMatch_V4_2",
    "VerifiedProductNameMatch",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

AuditColumns = [
    Column
    for Column in AuditColumns
    if Column in UnknownModelDf.columns
]

AuditDf = UnknownModelDf[AuditColumns].copy()

OutputFile = (
    AuditFolder /
    "Unknown_Product_Models_Audit_V4_2.csv"
)

AuditDf.to_csv(OutputFile, index=False)

print("=" * 65)
print("UNKNOWN PRODUCT MODEL AUDIT V4.2")
print("=" * 65)

print(f"Total candidate pairs: {len(CandidateDf)}")
print(f"Unknown model records: {len(UnknownModelDf)}")
print(
    f"Unique CandidatePairIDs: "
    f"{UnknownModelDf['CandidatePairID'].nunique()}"
)

print(f"\nSaved: {OutputFile.resolve()}")
print("\nAudit completed successfully.")