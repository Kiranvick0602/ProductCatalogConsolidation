import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

OutputFolder = Path("data/output")

V3File = OutputFolder / "CandidatePairs_ProductModelVerification_V3.csv"

V4_1File = OutputFolder / "CandidatePairs_ProductModelVerification_V4_1.csv"

AuditFolder = (
    OutputFolder /
    "quality" /
    "product_model_audit"
)

AuditFolder.mkdir(parents=True, exist_ok=True)

# ============================================================
# READ INPUT FILES
# ============================================================

V3Df = pd.read_csv(V3File, dtype=str, keep_default_na=False)

V4_1Df = pd.read_csv(V4_1File, dtype=str, keep_default_na=False)

# ============================================================
# PREPARE V3 DATA
# ============================================================

V3Columns = [
    "CandidatePairID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "VerifiedProductModelMatch"
]

V3ComparisonDf = V3Df[V3Columns].copy()

V3ComparisonDf.rename(
    columns={
        "VerifiedProductModelMatch": "V3_Decision"
    },
    inplace=True
)

# ============================================================
# PREPARE V4.1 DATA
# ============================================================

V4_1Columns = [
    "CandidatePairID",
    "StyleHaus_NormalizedProductModel_V4_1",
    "UrbanThread_NormalizedProductModel_V4_1",
    "VerifiedProductModelMatch_V4_1"
]

V4_1ComparisonDf = V4_1Df[V4_1Columns].copy()

V4_1ComparisonDf.rename(
    columns={
        "VerifiedProductModelMatch_V4_1": "V4_1_Decision"
    },
    inplace=True
)

# ============================================================
# COMPARE CLASSIFICATIONS
# ============================================================

ComparisonDf = V3ComparisonDf.merge(
    V4_1ComparisonDf,
    on="CandidatePairID",
    how="inner",
    validate="one_to_one"
)

ComparisonDf["ClassificationChanged"] = (
    ComparisonDf["V3_Decision"] !=
    ComparisonDf["V4_1_Decision"]
)

# ============================================================
# TRANSITION SUMMARY
# ============================================================

TransitionSummaryDf = (
    ComparisonDf
    .groupby(
        ["V3_Decision", "V4_1_Decision"]
    )
    .size()
    .reset_index(name="RecordCount")
)

TransitionSummaryFile = (
    AuditFolder /
    "V3_V4_1_Transition_Summary.csv"
)

TransitionSummaryDf.to_csv(
    TransitionSummaryFile,
    index=False
)

# ============================================================
# CHANGED CLASSIFICATIONS
# ============================================================

ChangedDf = ComparisonDf[
    ComparisonDf["ClassificationChanged"]
].copy()

ChangedFile = (
    AuditFolder /
    "V3_V4_1_Changed_Classifications.csv"
)

ChangedDf.to_csv(
    ChangedFile,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print("=" * 68)
print("V3 VS V4.1 PRODUCT MODEL COMPARISON")
print("=" * 68)

print(f"V3 records: {len(V3Df)}")
print(f"V4.1 records: {len(V4_1Df)}")
print(f"Matched CandidatePairIDs: {len(ComparisonDf)}")
print(f"Changed classifications: {len(ChangedDf)}")

print("\nTRANSITION SUMMARY")

print(
    TransitionSummaryDf.to_string(index=False)
)

print("\nSaved:")
print(TransitionSummaryFile)
print(ChangedFile)

print("\nComparison completed successfully.")