from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]

InputFile = str(ProjectRoot / "data/output/CandidatePairs_MaterialVerification.csv")

CandidateDf = pd.read_csv(InputFile)

VerificationColumns = [
    "VerifiedBrandMatch",
    "VerifiedProductNameMatch",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

print("\nATTRIBUTE VERIFICATION DISTRIBUTION")
print("=" * 70)

for Column in VerificationColumns:

    print(f"\n{Column}")

    print(
        CandidateDf[Column]
        .fillna("NULL")
        .value_counts(dropna=False)
        .to_string()
    )

    print("-" * 50)