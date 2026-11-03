import sys
from pathlib import Path
import pandas as pd

ProjectDirectory = Path(__file__).resolve().parents[2]
if str(ProjectDirectory) not in sys.path:
    sys.path.insert(0, str(ProjectDirectory))

from ai_matching.matching.attribute_verification import VerifyBrand
InputPath = ProjectDirectory / "data" / "output" / "CandidatePairs_EmbeddingSimilarity.csv"
OutputPath = ProjectDirectory / "data" / "output" / "CandidatePairs_BrandVerification_V2.csv"
EXPECTED_CANDIDATE_COUNT = 185

CandidatePairsDf = pd.read_csv(InputPath, dtype=str, keep_default_na=False)

RequiredColumns = ["CandidatePairID", "StyleHaus_Brand", "UrbanThread_Brand"]
MissingColumns = [Column for Column in RequiredColumns if Column not in CandidatePairsDf.columns]
if MissingColumns:
    raise ValueError(f"Missing required columns: {MissingColumns}")
if len(CandidatePairsDf) != EXPECTED_CANDIDATE_COUNT:
    raise ValueError(f"Expected {EXPECTED_CANDIDATE_COUNT} candidates; found {len(CandidatePairsDf)}")
if CandidatePairsDf["CandidatePairID"].eq("").any() or CandidatePairsDf["CandidatePairID"].duplicated().any():
    raise ValueError("CandidatePairID is blank or duplicated.")

CandidatePairsDf["VerifiedBrandMatch"] = CandidatePairsDf.apply(
    lambda Row: VerifyBrand(Row["StyleHaus_Brand"], Row["UrbanThread_Brand"]), axis=1
)

print("BRAND VERIFICATION V2")
print(CandidatePairsDf["VerifiedBrandMatch"].value_counts(dropna=False).to_string())
CandidatePairsDf.to_csv(OutputPath, index=False, encoding="utf-8-sig")
print(f"Saved: {OutputPath}")
