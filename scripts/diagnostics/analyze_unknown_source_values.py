from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]

InputFile = str(ProjectRoot / "data/output/llm/UnknownMatchAttributeAnalysis.csv")

Df = pd.read_csv(InputFile)

Attributes = {
    "ProductName": (
        "StyleHaus_ProductName",
        "UrbanThread_ProductName",
        "VerifiedProductNameMatch"
    ),
    "Color": (
        "StyleHaus_Color",
        "UrbanThread_Color",
        "VerifiedColorMatch"
    ),
    "Size": (
        "StyleHaus_Size",
        "UrbanThread_Size",
        "VerifiedSizeMatch"
    ),
    "Material": (
        "StyleHaus_Material",
        "UrbanThread_Material",
        "VerifiedMaterialMatch"
    )
}

print("\nUNKNOWN SOURCE VALUE ANALYSIS")
print("=" * 75)

for Attribute, Columns in Attributes.items():

    StyleHausColumn, UrbanThreadColumn, VerificationColumn = Columns

    UnknownDf = Df[
        Df[VerificationColumn] == "UNKNOWN"
    ]

    StyleHausValues = UnknownDf[StyleHausColumn].fillna("").astype(str).str.strip()
    UrbanThreadValues = UnknownDf[UrbanThreadColumn].fillna("").astype(str).str.strip()

    BothAvailable = (
        (StyleHausValues != "") &
        (UrbanThreadValues != "")
    )

    BothMissing = (
        (StyleHausValues == "") &
        (UrbanThreadValues == "")
    )

    OneMissing = (
        (StyleHausValues == "") ^
        (UrbanThreadValues == "")
    )

    print(f"\nATTRIBUTE: {Attribute}")
    print("-" * 75)

    print("Unknown Records:", len(UnknownDf))
    print("Both Values Available:", int(BothAvailable.sum()))
    print("Both Values Missing:", int(BothMissing.sum()))
    print("One Value Missing:", int(OneMissing.sum()))

    print("\nSample Records:")

    Sample = UnknownDf[
        [
            "CandidatePairID",
            StyleHausColumn,
            UrbanThreadColumn
        ]
    ].head(5)

    print(Sample.to_string(index=False))