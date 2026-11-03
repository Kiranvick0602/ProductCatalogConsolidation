import pandas as pd
from pathlib import Path

OutputFolder = Path("data/output")

V3File = OutputFolder / "CandidatePairs_ProductModelVerification_V3.csv"
V4File = OutputFolder / "CandidatePairs_ProductModelVerification_V4.csv"

AuditFolder = OutputFolder / "quality" / "product_model_audit"
AuditFolder.mkdir(parents=True, exist_ok=True)

V3Df = pd.read_csv(V3File, dtype=str, keep_default_na=False)
V4Df = pd.read_csv(V4File, dtype=str, keep_default_na=False)

ComparisonDf = V3Df[
    [
        "CandidatePairID",
        "StyleHaus_ProductName",
        "UrbanThread_ProductName",
        "VerifiedProductModelMatch"
    ]
].merge(
    V4Df[
        [
            "CandidatePairID",
            "StyleHaus_NormalizedProductModel_V4",
            "UrbanThread_NormalizedProductModel_V4",
            "VerifiedProductModelMatch_V4"
        ]
    ],
    on="CandidatePairID",
    how="inner",
    validate="one_to_one"
)

ComparisonDf.rename(
    columns={
        "VerifiedProductModelMatch": "V3_Decision",
        "VerifiedProductModelMatch_V4": "V4_Decision"
    },
    inplace=True
)

ComparisonDf["ClassificationChanged"] = (
    ComparisonDf["V3_Decision"] != ComparisonDf["V4_Decision"]
)

# Transition summary
TransitionSummary = (
    ComparisonDf
    .groupby(
        ["V3_Decision", "V4_Decision"]
    )
    .size()
    .reset_index(name="RecordCount")
)

TransitionSummary.to_csv(
    AuditFolder / "V3_V4_Transition_Summary.csv",
    index=False
)

# Changed classifications
ChangedDf = ComparisonDf[
    ComparisonDf["ClassificationChanged"]
].copy()

ChangedDf.to_csv(
    AuditFolder / "V3_V4_Changed_Classifications.csv",
    index=False
)

print("=" * 65)
print("V3 VS V4 PRODUCT MODEL COMPARISON")
print("=" * 65)

print(f"V3 records: {len(V3Df)}")
print(f"V4 records: {len(V4Df)}")
print(f"Matched CandidatePairIDs: {len(ComparisonDf)}")
print(f"Changed classifications: {len(ChangedDf)}")

print("\nTRANSITION SUMMARY")
print(TransitionSummary.to_string(index=False))

print("\nSaved:")
print(AuditFolder / "V3_V4_Transition_Summary.csv")
print(AuditFolder / "V3_V4_Changed_Classifications.csv")