from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]


# ============================================================
# CONFIGURATION
# ============================================================

InputFilePath = (
    "data/output/CandidatePairs_MaterialVerification.csv"
)


# ============================================================
# LOAD CANDIDATE DATA
# ============================================================

CandidateDf = pd.read_csv(
    InputFilePath,
    dtype=str,
    keep_default_na=False
)

print(f"Total Candidate Pairs: {len(CandidateDf)}")


# ============================================================
# EMBEDDING SIMILARITY ANALYSIS
# ============================================================

CandidateDf["EmbeddingSimilarity"] = pd.to_numeric(
    CandidateDf["EmbeddingSimilarity"],
    errors="coerce"
)

print("\nEMBEDDING SIMILARITY SUMMARY")
print("-" * 60)

print(
    CandidateDf["EmbeddingSimilarity"].describe()
)


# ============================================================
# PRODUCT NAME SIMILARITY ANALYSIS
# ============================================================

CandidateDf["ProductNameSimilarity"] = pd.to_numeric(
    CandidateDf["ProductNameSimilarity"],
    errors="coerce"
)

print("\nPRODUCT NAME SIMILARITY SUMMARY")
print("-" * 60)

print(
    CandidateDf["ProductNameSimilarity"].describe()
)


# ============================================================
# ATTRIBUTE VERIFICATION SUMMARY
# ============================================================

VerificationColumns = [
    "VerifiedBrandMatch",
    "VerifiedProductNameMatch",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

for ColumnName in VerificationColumns:

    print(f"\n{ColumnName}")
    print("-" * 60)

    print(
        CandidateDf[ColumnName].value_counts(
            dropna=False
        )
    )


# ============================================================
# LOWEST EMBEDDING SIMILARITY PAIRS
# ============================================================

print("\nLOWEST 15 EMBEDDING SIMILARITY PAIRS")
print("-" * 60)

LowestSimilarityDf = CandidateDf.nsmallest(
    15,
    "EmbeddingSimilarity"
)

DisplayColumns = [
    "CandidatePairID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "EmbeddingSimilarity",
    "ProductNameSimilarity",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

print(
    LowestSimilarityDf[DisplayColumns].to_string(
        index=False
    )
)


# ============================================================
# HIGHEST EMBEDDING SIMILARITY PAIRS
# ============================================================

print("\nHIGHEST 15 EMBEDDING SIMILARITY PAIRS")
print("-" * 60)

HighestSimilarityDf = CandidateDf.nlargest(
    15,
    "EmbeddingSimilarity"
)

print(
    HighestSimilarityDf[DisplayColumns].to_string(
        index=False
    )
)