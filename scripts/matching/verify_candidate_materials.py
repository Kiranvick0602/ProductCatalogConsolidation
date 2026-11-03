import sys
from pathlib import Path
import pandas as pd

ProjectDirectory = Path(__file__).resolve().parents[2]
if str(ProjectDirectory) not in sys.path:
    sys.path.insert(0, str(ProjectDirectory))

from ai_matching.matching.attribute_verification import VerifyMaterial
InputPath = ProjectDirectory / "data" / "output" / "CandidatePairs_SizeVerification_V2.csv"
OutputPath = ProjectDirectory / "data" / "output" / "CandidatePairs_MaterialVerification_V2.csv"
EXPECTED_CANDIDATE_COUNT = 185

CandidateDf = pd.read_csv(InputPath, dtype=str, keep_default_na=False)
RequiredColumns = ["CandidatePairID", "StyleHaus_Material", "UrbanThread_Material"]
MissingColumns = [Column for Column in RequiredColumns if Column not in CandidateDf.columns]
if MissingColumns:
    raise ValueError(f"Missing required columns: {MissingColumns}")
if len(CandidateDf) != EXPECTED_CANDIDATE_COUNT:
    raise ValueError(f"Expected {EXPECTED_CANDIDATE_COUNT} candidates; found {len(CandidateDf)}")
if CandidateDf["CandidatePairID"].eq("").any() or CandidateDf["CandidatePairID"].duplicated().any():
    raise ValueError("CandidatePairID is blank or duplicated.")

CandidateDf["VerifiedMaterialMatch"] = CandidateDf.apply(
    lambda Row: VerifyMaterial(Row["StyleHaus_Material"], Row["UrbanThread_Material"]), axis=1
)

print("MATERIAL VERIFICATION V2 (SUPPORTING ATTRIBUTE)")
print(CandidateDf["VerifiedMaterialMatch"].value_counts(dropna=False).to_string())
CandidateDf.to_csv(OutputPath, index=False, encoding="utf-8-sig")
print(f"Saved: {OutputPath}")
