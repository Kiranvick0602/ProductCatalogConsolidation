import pandas as pd
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]

OutputFolder = ProjectRoot / Path("data/output")

Attributes = {
    "Brand": (
        "CandidatePairs_BrandVerification.csv",
        "CandidatePairs_BrandVerification_V2.csv",
        "VerifiedBrandMatch"
    ),
    "ProductName": (
        "CandidatePairs_ProductNameVerification.csv",
        "CandidatePairs_ProductNameVerification_V2.csv",
        "VerifiedProductNameMatch"
    ),
    "Category": (
        "CandidatePairs_CategoryVerification.csv",
        "CandidatePairs_CategoryVerification_V2.csv",
        "VerifiedCategoryMatch"
    ),
    "Color": (
        "CandidatePairs_ColorVerification.csv",
        "CandidatePairs_ColorVerification_V2.csv",
        "VerifiedColorMatch"
    ),
    "Size": (
        "CandidatePairs_SizeVerification.csv",
        "CandidatePairs_SizeVerification_V2.csv",
        "VerifiedSizeMatch"
    ),
    "Material": (
        "CandidatePairs_MaterialVerification.csv",
        "CandidatePairs_MaterialVerification_V2.csv",
        "VerifiedMaterialMatch"
    )
}

for Attribute, Files in Attributes.items():

    V1File, V2File, VerificationColumn = Files

    V1Df = pd.read_csv(OutputFolder / V1File)
    V2Df = pd.read_csv(OutputFolder / V2File)

    if set(V1Df["CandidatePairID"]) != set(V2Df["CandidatePairID"]):
        raise ValueError(f"Candidate IDs differ for {Attribute}")

    V1Counts = V1Df[VerificationColumn].value_counts()
    V2Counts = V2Df[VerificationColumn].value_counts()

    Summary = pd.DataFrame({
        "V1": V1Counts,
        "V2": V2Counts
    }).fillna(0).astype(int)

    print("\n" + "=" * 65)
    print(f"{Attribute.upper()} VERIFICATION COMPARISON")
    print("=" * 65)

    print(Summary.to_string())