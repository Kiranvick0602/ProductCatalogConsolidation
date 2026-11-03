import pandas as pd
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]

OutputFolder = ProjectRoot / Path("data/output")

VerificationFiles = [
    "CandidatePairs_BrandVerification.csv",
    "CandidatePairs_ProductNameVerification.csv",
    "CandidatePairs_CategoryVerification.csv",
    "CandidatePairs_ColorVerification.csv",
    "CandidatePairs_SizeVerification.csv",
    "CandidatePairs_MaterialVerification.csv"
]

for FileName in VerificationFiles:

    FilePath = OutputFolder / FileName
    Df = pd.read_csv(FilePath)

    print("\n" + "=" * 80)
    print(f"FILE: {FileName}")
    print("=" * 80)

    print(f"Rows: {len(Df)}")
    print("Columns:")

    for Column in Df.columns:
        print(f"  - {Column}")