import sys
from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parent.parent
OutputFolder = ProjectRoot / "data" / "output"
AuditFolder = OutputFolder / "quality" / "product_model_audit"
AuditFolder.mkdir(parents=True, exist_ok=True)

V4_2File = OutputFolder / "CandidatePairs_ProductModelVerification_V4_2.csv"
V4_3File = OutputFolder / "CandidatePairs_ProductModelVerification_V4_3.csv"

V4_2Df = pd.read_csv(V4_2File, dtype=str, keep_default_na=False)
V4_3Df = pd.read_csv(V4_3File, dtype=str, keep_default_na=False)

ComparisonDf = V4_2Df[
    ["CandidatePairID", "StyleHaus_ProductName", "UrbanThread_ProductName",
     "VerifiedProductModelMatch_V4_2"]
].merge(
    V4_3Df[
        ["CandidatePairID", "StyleHaus_NormalizedProductModel_V4_3",
         "UrbanThread_NormalizedProductModel_V4_3",
         "VerifiedProductModelMatch_V4_3"]
    ],
    on="CandidatePairID",
    how="inner",
    validate="one_to_one"
)

ComparisonDf["ClassificationChanged"] = (
    ComparisonDf["VerifiedProductModelMatch_V4_2"]
    != ComparisonDf["VerifiedProductModelMatch_V4_3"]
)

TransitionSummaryDf = (
    ComparisonDf.groupby(
        ["VerifiedProductModelMatch_V4_2", "VerifiedProductModelMatch_V4_3"]
    ).size().reset_index(name="RecordCount")
)

ChangedDf = ComparisonDf[ComparisonDf["ClassificationChanged"]].copy()
SummaryFile = AuditFolder / "V4_2_V4_3_Transition_Summary.csv"
ChangedFile = AuditFolder / "V4_2_V4_3_Changed_Classifications.csv"
TransitionSummaryDf.to_csv(SummaryFile, index=False)
ChangedDf.to_csv(ChangedFile, index=False)

print("=" * 68)
print("V4.2 VS V4.3 COMPARISON")
print("=" * 68)
print(f"V4.2 records: {len(V4_2Df)}")
print(f"V4.3 records: {len(V4_3Df)}")
print(f"Matched CandidatePairIDs: {len(ComparisonDf)}")
print(f"Changed classifications: {len(ChangedDf)}")
print("\nTRANSITION SUMMARY")
print(TransitionSummaryDf.to_string(index=False))
print(f"\nSaved: {SummaryFile}")
print(ChangedFile)
