import sys
from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parent.parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.product_model_verification import VerifyProductModel

InputFile = ProjectRoot / "data" / "output" / "CandidatePairs_ProductModelVerification_V3.csv"
OutputFile = ProjectRoot / "data" / "output" / "CandidatePairs_ProductModelVerification_V4.csv"

CandidateDf = pd.read_csv(InputFile, dtype=str, keep_default_na=False)

RequiredColumns = [
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
]
MissingColumns = [Column for Column in RequiredColumns if Column not in CandidateDf.columns]
if MissingColumns:
    raise ValueError(f"Missing required columns: {MissingColumns}")

Results = CandidateDf.apply(
    lambda Row: VerifyProductModel(
        Row.get("StyleHaus_ProductName", ""),
        Row.get("UrbanThread_ProductName", ""),
        Row.get("StyleHaus_Brand", ""),
        Row.get("UrbanThread_Brand", ""),
    ),
    axis=1
)

CandidateDf["StyleHaus_NormalizedProductModel_V4"] = [Result[1] for Result in Results]
CandidateDf["UrbanThread_NormalizedProductModel_V4"] = [Result[2] for Result in Results]
CandidateDf["VerifiedProductModelMatch_V4"] = [Result[0] for Result in Results]

CandidateDf.to_csv(OutputFile, index=False)

print("=" * 68)
print("PRODUCT MODEL VERIFICATION V4")
print("=" * 68)
print(f"Total candidate pairs: {len(CandidateDf)}")
print("\nClassification counts:")
print(CandidateDf["VerifiedProductModelMatch_V4"].value_counts(dropna=False).to_string())
print(f"\nUnique CandidatePairIDs: {CandidateDf['CandidatePairID'].nunique() if 'CandidatePairID' in CandidateDf.columns else 'N/A'}")
print(f"Saved: {OutputFile}")
print("\nV4 verification completed.")
