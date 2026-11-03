import sys
from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parent.parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.color_verification import verify_color

InputPath = ProjectRoot / "data" / "output" / "CandidatePairs_ProductModelVerification_V4_3_1.csv"
OutputPath = ProjectRoot / "data" / "output" / "CandidatePairs_ColorVerification_V3.csv"
AuditPath = ProjectRoot / "data" / "output" / "quality" / "color_verification_audit" / "ColorVerification_V2_vs_V3_Changed.csv"
SummaryPath = ProjectRoot / "data" / "output" / "quality" / "color_verification_audit" / "ColorVerification_V3_Summary.csv"

if not InputPath.exists():
    raise FileNotFoundError(f"Input file not found: {InputPath}")

Df = pd.read_csv(InputPath)

RequiredColumns = ["StyleHaus_Color", "UrbanThread_Color"]
MissingColumns = [C for C in RequiredColumns if C not in Df.columns]
if MissingColumns:
    raise ValueError(f"Missing required columns: {MissingColumns}")

Results = Df.apply(
    lambda R: verify_color(R["StyleHaus_Color"], R["UrbanThread_Color"]),
    axis=1
)

Df["VerifiedColorMatch_V3"] = Results.map(lambda X: X[0])
Df["StyleHaus_NormalizedColor_V3"] = Results.map(lambda X: X[1])
Df["UrbanThread_NormalizedColor_V3"] = Results.map(lambda X: X[2])

OutputPath.parent.mkdir(parents=True, exist_ok=True)
Df.to_csv(OutputPath, index=False)

Summary = (
    Df["VerifiedColorMatch_V3"]
    .value_counts(dropna=False)
    .rename_axis("VerifiedColorMatch_V3")
    .reset_index(name="RecordCount")
)
SummaryPath.parent.mkdir(parents=True, exist_ok=True)
Summary.to_csv(SummaryPath, index=False)

if "VerifiedColorMatch" in Df.columns:
    Changed = Df.loc[
        Df["VerifiedColorMatch"].fillna("") != Df["VerifiedColorMatch_V3"].fillna(""),
        [
            "CandidatePairID",
            "StyleHaus_ProductName",
            "UrbanThread_ProductName",
            "StyleHaus_Color",
            "UrbanThread_Color",
            "VerifiedColorMatch",
            "VerifiedColorMatch_V3",
            "StyleHaus_NormalizedColor_V3",
            "UrbanThread_NormalizedColor_V3",
        ],
    ].copy()
else:
    Changed = pd.DataFrame()

Changed.to_csv(AuditPath, index=False)

print("=" * 68)
print("COLOR VERIFICATION V3")
print("=" * 68)
print(f"Candidate pairs: {len(Df)}")
print("\nClassification counts:")
print(Summary.to_string(index=False))
print(f"\nChanged classifications vs existing: {len(Changed)}")
print(f"Saved output: {OutputPath}")
print(f"Saved summary: {SummaryPath}")
print(f"Saved changed-record audit: {AuditPath}")
