import sys
from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parent.parent
OutputFolder = ProjectRoot / "data" / "output"
AuditFolder = OutputFolder / "quality" / "product_model_audit"
AuditFolder.mkdir(parents=True, exist_ok=True)

V4_1File = OutputFolder / "CandidatePairs_ProductModelVerification_V4_1.csv"
V4_2File = OutputFolder / "CandidatePairs_ProductModelVerification_V4_2.csv"

V4_1Df = pd.read_csv(V4_1File, dtype=str, keep_default_na=False)
V4_2Df = pd.read_csv(V4_2File, dtype=str, keep_default_na=False)

ComparisonDf = V4_1Df[
    ["CandidatePairID", "StyleHaus_ProductName", "UrbanThread_ProductName",
     "VerifiedProductModelMatch_V4_1"]
].merge(
    V4_2Df[
        ["CandidatePairID", "StyleHaus_NormalizedProductModel_V4_2",
         "UrbanThread_NormalizedProductModel_V4_2",
         "VerifiedProductModelMatch_V4_2"]
    ],
    on="CandidatePairID",
    how="inner",
    validate="one_to_one"
)

ComparisonDf["ClassificationChanged"] = (
    ComparisonDf["VerifiedProductModelMatch_V4_1"]
    != ComparisonDf["VerifiedProductModelMatch_V4_2"]
)

TransitionSummaryDf = (
    ComparisonDf.groupby(
        ["VerifiedProductModelMatch_V4_1", "VerifiedProductModelMatch_V4_2"]
    ).size().reset_index(name="RecordCount")
)

ChangedDf = ComparisonDf[ComparisonDf["ClassificationChanged"]].copy()

SummaryFile = AuditFolder / "V4_1_V4_2_Transition_Summary.csv"
ChangedFile = AuditFolder / "V4_1_V4_2_Changed_Classifications.csv"

TransitionSummaryDf.to_csv(SummaryFile, index=False)
ChangedDf.to_csv(ChangedFile, index=False)

print("=" * 68)
print("V4.1 VS V4.2 COMPARISON")
print("=" * 68)
print(f"V4.1 records: {len(V4_1Df)}")
print(f"V4.2 records: {len(V4_2Df)}")
print(f"Matched CandidatePairIDs: {len(ComparisonDf)}")
print(f"Changed classifications: {len(ChangedDf)}")
print("\nTRANSITION SUMMARY")
print(TransitionSummaryDf.to_string(index=False))
print(f"\nSaved: {SummaryFile}")
print(ChangedFile)
