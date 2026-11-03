import pandas as pd
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]

V3Path = ProjectRoot / "data/output/CandidatePairs_ColorVerification_V3.csv"
V3_1Path = ProjectRoot / "data/output/CandidatePairs_ColorVerification_V3_1.csv"

AuditPath = (
    ProjectRoot
    / "data/output/quality/color_verification_audit/"
    / "ColorVerification_V3_vs_V3_1_Changed.csv"
)

V3Df = pd.read_csv(V3Path)
V3_1Df = pd.read_csv(V3_1Path)

ComparisonDf = V3Df[
    ["CandidatePairID", "VerifiedColorMatch_V3"]
].merge(
    V3_1Df[
        ["CandidatePairID", "VerifiedColorMatch_V3_1"]
    ],
    on="CandidatePairID",
    how="inner"
)

ChangedDf = ComparisonDf[
    ComparisonDf["VerifiedColorMatch_V3"]
    != ComparisonDf["VerifiedColorMatch_V3_1"]
]

AuditPath.parent.mkdir(parents=True, exist_ok=True)
ChangedDf.to_csv(AuditPath, index=False)

print("V3 VS V3.1 COMPARISON")
print("=" * 50)
print("V3 Records:", len(V3Df))
print("V3.1 Records:", len(V3_1Df))
print("Changed classifications:", len(ChangedDf))

print("\nTransition Summary:")

print(
    pd.crosstab(
        ComparisonDf["VerifiedColorMatch_V3"],
        ComparisonDf["VerifiedColorMatch_V3_1"]
    )
)

print("\nSaved:", AuditPath)