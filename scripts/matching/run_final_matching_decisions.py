import sys
from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.final_decision import decide_row

InputPath = ProjectRoot / "data" / "output" / "CandidatePairs_ColorVerification_V3_1.csv"
OutputPath = ProjectRoot / "data" / "output" / "CandidatePairs_FinalMatchingDecisions.csv"
SummaryPath = ProjectRoot / "data" / "output" / "quality" / "final_matching" / "FinalMatchingDecision_Summary.csv"

if not InputPath.exists():
    raise FileNotFoundError(f"Input file not found: {InputPath}")

Df = pd.read_csv(InputPath)
Required = [
    "CandidatePairID", "VerifiedBrandMatch",
    "VerifiedProductModelMatch_V4_3_1", "VerifiedColorMatch_V3_1",
    "VerifiedSizeMatch", "StyleHaus_Size", "UrbanThread_Size"
]
Missing = [C for C in Required if C not in Df.columns]
if Missing:
    raise ValueError(f"Missing required columns: {Missing}")

Decisions = Df.apply(decide_row, axis=1)
Df["FinalVerifiedSizeMatch"] = Decisions["FinalVerifiedSizeMatch"]
Df["FinalMatchDecision"] = Decisions["FinalMatchDecision"]
Df["DecisionReason"] = Decisions["DecisionReason"]

if Df["CandidatePairID"].duplicated().any():
    raise ValueError("Duplicate CandidatePairID values found.")
if len(Df) != 185:
    print(f"WARNING: Expected 185 candidate pairs; found {len(Df)}.")

OutputPath.parent.mkdir(parents=True, exist_ok=True)
SummaryPath.parent.mkdir(parents=True, exist_ok=True)
Df.to_csv(OutputPath, index=False)

Summary = Df["FinalMatchDecision"].value_counts().rename_axis(
    "FinalMatchDecision"
).reset_index(name="RecordCount")
Summary.to_csv(SummaryPath, index=False)

print("=" * 68)
print("FINAL MATCHING DECISION ENGINE")
print("=" * 68)
print(f"Candidate pairs: {len(Df)}")
print("\nFinal decision counts:")
print(Summary.to_string(index=False))
print("\nFinal size verification counts:")
print(Df["FinalVerifiedSizeMatch"].value_counts().to_string())
print(f"\nSaved decisions: {OutputPath}")
print(f"Saved summary: {SummaryPath}")
