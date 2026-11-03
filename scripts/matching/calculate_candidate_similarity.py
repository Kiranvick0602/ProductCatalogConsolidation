import sys
import json
from pathlib import Path
import pandas as pd

ProjectDirectory = Path(__file__).resolve().parents[2]
if str(ProjectDirectory) not in sys.path:
    sys.path.insert(0, str(ProjectDirectory))

from ai_matching.matching.cosine_similarity import (
    CalculateCosineSimilarity
)


# ============================================================
# CONFIGURATION
# ============================================================


CandidatePairsPath = (
    ProjectDirectory
    / "data"
    / "output"
    / "CandidatePairs_CanonicalText.csv"
)

ProductEmbeddingsPath = (
    ProjectDirectory
    / "data"
    / "embeddings"
    / "ProductEmbeddings.jsonl"
)

OutputPath = (
    ProjectDirectory
    / "data"
    / "output"
    / "CandidatePairs_EmbeddingSimilarity.csv"
)

ExpectedEmbeddingDimension = 768


# ============================================================
# STEP 1: LOAD CANDIDATE PAIRS
# ============================================================

print("\n" + "=" * 70)
print("CANDIDATE PRODUCT COSINE SIMILARITY CALCULATION")
print("=" * 70)

CandidatePairsDf = pd.read_csv(
    CandidatePairsPath,
    dtype=str,
    keep_default_na=False
)

print(f"\nCandidate Pairs Loaded: {len(CandidatePairsDf)}")


# ============================================================
# STEP 2: LOAD PRODUCT EMBEDDINGS
# ============================================================

EmbeddingLookup = {}

with open(
    ProductEmbeddingsPath,
    "r",
    encoding="utf-8"
) as File:

    for Line in File:

        if not Line.strip():
            continue

        Record = json.loads(Line)

        ProductKey = (
            Record["Source"],
            Record["ProductID"]
        )

        if ProductKey in EmbeddingLookup:

            raise ValueError(
                f"Duplicate embedding found for {ProductKey}"
            )

        Embedding = Record["Embedding"]

        if len(Embedding) != ExpectedEmbeddingDimension:

            raise ValueError(
                f"Invalid embedding dimension for {ProductKey}"
            )

        EmbeddingLookup[ProductKey] = Embedding


print(f"Unique Product Embeddings Loaded: {len(EmbeddingLookup)}")


# ============================================================
# STEP 3: CALCULATE COSINE SIMILARITY
# ============================================================

EmbeddingSimilarities = []

MissingEmbeddings = []

for Index, Row in CandidatePairsDf.iterrows():

    StyleHausProductID = Row["StyleHaus_ProductID"]

    UrbanThreadProductID = Row["UrbanThread_ProductID"]

    StyleHausKey = (
        "StyleHaus",
        StyleHausProductID
    )

    UrbanThreadKey = (
        "UrbanThread",
        UrbanThreadProductID
    )

    # Retrieve StyleHaus embedding
    StyleHausEmbedding = EmbeddingLookup.get(
        StyleHausKey
    )

    # Retrieve UrbanThread embedding
    UrbanThreadEmbedding = EmbeddingLookup.get(
        UrbanThreadKey
    )

    # Check whether both embeddings exist
    if (
        StyleHausEmbedding is None
        or UrbanThreadEmbedding is None
    ):

        MissingEmbeddings.append({
            "CandidatePairID": Row["CandidatePairID"],
            "StyleHaus_ProductID": StyleHausProductID,
            "UrbanThread_ProductID": UrbanThreadProductID
        })

        EmbeddingSimilarities.append(None)

        continue

    # Calculate cosine similarity
    Similarity = CalculateCosineSimilarity(
        StyleHausEmbedding,
        UrbanThreadEmbedding
    )

    EmbeddingSimilarities.append(Similarity)

    if (Index + 1) % 25 == 0:

        print(
            f"Processed {Index + 1}/{len(CandidatePairsDf)} "
            f"candidate pairs"
        )


# ============================================================
# STEP 4: ADD SIMILARITY COLUMN
# ============================================================

CandidatePairsDf["EmbeddingSimilarity"] = (
    EmbeddingSimilarities
)


# ============================================================
# STEP 5: VALIDATE RESULTS
# ============================================================

TotalCandidatePairs = len(CandidatePairsDf)

ValidSimilarityCount = (
    CandidatePairsDf["EmbeddingSimilarity"].notna().sum()
)

MissingSimilarityCount = len(MissingEmbeddings)

InvalidSimilarityCount = (
    (
        CandidatePairsDf["EmbeddingSimilarity"].dropna() < -1
    )
    |
    (
        CandidatePairsDf["EmbeddingSimilarity"].dropna() > 1
    )
).sum()

DuplicateCandidatePairCount = (
    CandidatePairsDf["CandidatePairID"].duplicated().sum()
)

print("\n" + "-" * 70)
print("COSINE SIMILARITY VALIDATION")
print("-" * 70)

print(f"Total Candidate Pairs       : {TotalCandidatePairs}")
print(f"Valid Similarity Scores     : {ValidSimilarityCount}")
print(f"Missing Embeddings          : {MissingSimilarityCount}")
print(f"Invalid Similarity Scores   : {InvalidSimilarityCount}")
print(f"Duplicate Candidate Pairs   : {DuplicateCandidatePairCount}")


# ============================================================
# STEP 6: SAVE OUTPUT
# ============================================================

if (
    TotalCandidatePairs != 185
    or ValidSimilarityCount != TotalCandidatePairs
    or MissingSimilarityCount != 0
    or InvalidSimilarityCount != 0
    or DuplicateCandidatePairCount != 0
):

    raise ValueError(
        "Cosine similarity validation failed. "
        "Output file was not saved."
    )


CandidatePairsDf.to_csv(
    OutputPath,
    index=False
)


# ============================================================
# STEP 7: DISPLAY SUMMARY
# ============================================================

print("\n" + "-" * 70)
print("SIMILARITY SCORE SUMMARY")
print("-" * 70)

print(
    CandidatePairsDf["EmbeddingSimilarity"].describe()
)

print("\nSample Candidate Similarity Scores:")

print(
    CandidatePairsDf[
        [
            "CandidatePairID",
            "StyleHaus_ProductID",
            "UrbanThread_ProductID",
            "EmbeddingSimilarity"
        ]
    ].head(10).to_string(index=False)
)

print("\n" + "=" * 70)
print("COSINE SIMILARITY CALCULATION COMPLETED SUCCESSFULLY")
print("=" * 70)

print(f"\nOutput File: {OutputPath}")