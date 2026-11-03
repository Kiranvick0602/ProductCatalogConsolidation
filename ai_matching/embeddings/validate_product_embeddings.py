import json
import hashlib
import math

import pandas as pd

from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

ProjectDirectory = Path(__file__).resolve().parents[2]

UniqueProductsPath = (
    ProjectDirectory
    / "data"
    / "embeddings"
    / "UniqueProducts.csv"
)

ProductEmbeddingsPath = (
    ProjectDirectory
    / "data"
    / "embeddings"
    / "ProductEmbeddings.jsonl"
)

FailedProductsPath = (
    ProjectDirectory
    / "data"
    / "embeddings"
    / "FailedProducts.jsonl"
)

ExpectedModelName = "text-embedding-nomic-embed-text-v1.5"

ExpectedTaskPrefix = "classification: "

ExpectedEmbeddingDimension = 768


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def CalculateTextHash(CanonicalText):

    return hashlib.sha256(
        CanonicalText.encode("utf-8")
    ).hexdigest()


def LoadExpectedProducts():

    ProductsDf = pd.read_csv(
        UniqueProductsPath,
        dtype=str,
        keep_default_na=False
    )

    ExpectedProducts = {}

    for _, Row in ProductsDf.iterrows():

        ProductKey = (
            Row["Source"],
            Row["ProductID"]
        )

        ExpectedProducts[ProductKey] = Row["CanonicalText"]

    return ExpectedProducts


# ============================================================
# STEP 1: LOAD EXPECTED PRODUCTS
# ============================================================

print("\n" + "=" * 65)
print("NOMIC EMBEDDING PERSISTENCE VALIDATION")
print("=" * 65)

ExpectedProducts = LoadExpectedProducts()

print(f"\nExpected Unique Products: {len(ExpectedProducts)}")


# ============================================================
# STEP 2: READ EMBEDDING CHECKPOINT
# ============================================================

EmbeddingRecords = []

InvalidJsonLines = []

with open(
    ProductEmbeddingsPath,
    "r",
    encoding="utf-8"
) as File:

    for LineNumber, Line in enumerate(File, start=1):

        if not Line.strip():
            continue

        try:

            Record = json.loads(Line)

            EmbeddingRecords.append(Record)

        except json.JSONDecodeError:

            InvalidJsonLines.append(LineNumber)


print(f"Persisted Embeddings: {len(EmbeddingRecords)}")


# ============================================================
# STEP 3: INITIALIZE VALIDATION COUNTERS
# ============================================================

DuplicateKeys = []

UnexpectedProducts = []

MissingProducts = []

InvalidDimensions = []

InvalidEmbeddingValues = []

InvalidModelNames = []

InvalidTaskPrefixes = []

InvalidTextHashes = []

MissingFields = []

SeenProductKeys = []


# ============================================================
# STEP 4: VALIDATE EACH EMBEDDING
# ============================================================

for Record in EmbeddingRecords:

    RequiredFields = [
        "Source",
        "ProductID",
        "TextHash",
        "ModelName",
        "TaskPrefix",
        "EmbeddingDimension",
        "Embedding",
        "GeneratedAt"
    ]

    Missing = [
        Field
        for Field in RequiredFields
        if Field not in Record
    ]

    if Missing:

        MissingFields.append({
            "ProductID": Record.get("ProductID"),
            "MissingFields": Missing
        })

        continue

    ProductKey = (
        Record["Source"],
        Record["ProductID"]
    )

    SeenProductKeys.append(ProductKey)

    # Check duplicate product keys

    if SeenProductKeys.count(ProductKey) > 1:

        DuplicateKeys.append(ProductKey)

    # Check whether the product exists in source data

    if ProductKey not in ExpectedProducts:

        UnexpectedProducts.append(ProductKey)

        continue

    # Check embedding dimension

    Embedding = Record["Embedding"]

    if (
        not isinstance(Embedding, list)
        or len(Embedding) != ExpectedEmbeddingDimension
        or Record["EmbeddingDimension"] != ExpectedEmbeddingDimension
    ):

        InvalidDimensions.append(ProductKey)

        continue

    # Check embedding values

    try:

        IsValidEmbedding = all(
            isinstance(Value, (int, float))
            and not isinstance(Value, bool)
            and math.isfinite(Value)
            for Value in Embedding
        )

        if not IsValidEmbedding:

            InvalidEmbeddingValues.append(ProductKey)

    except (TypeError, ValueError):

        InvalidEmbeddingValues.append(ProductKey)

    # Check model name

    if Record["ModelName"] != ExpectedModelName:

        InvalidModelNames.append(ProductKey)

    # Check task prefix

    if Record["TaskPrefix"] != ExpectedTaskPrefix:

        InvalidTaskPrefixes.append(ProductKey)

    # Check canonical text hash

    CanonicalText = ExpectedProducts[ProductKey]

    ExpectedHash = CalculateTextHash(CanonicalText)

    if Record["TextHash"] != ExpectedHash:

        InvalidTextHashes.append(ProductKey)


# ============================================================
# STEP 5: CHECK MISSING PRODUCTS
# ============================================================

PersistedProductKeys = set(SeenProductKeys)

ExpectedProductKeys = set(ExpectedProducts.keys())

MissingProducts = list(
    ExpectedProductKeys - PersistedProductKeys
)


# ============================================================
# STEP 6: CHECK FAILED PRODUCTS FILE
# ============================================================

FailedProductCount = 0

if FailedProductsPath.exists():

    with open(
        FailedProductsPath,
        "r",
        encoding="utf-8"
    ) as File:

        for Line in File:

            if Line.strip():

                FailedProductCount += 1


# ============================================================
# STEP 7: PRINT VALIDATION RESULTS
# ============================================================

ValidationResults = {

    "Expected Products": len(ExpectedProducts),

    "Persisted Embeddings": len(EmbeddingRecords),

    "Unique Persisted Products": len(PersistedProductKeys),

    "Duplicate Product Keys": len(DuplicateKeys),

    "Missing Products": len(MissingProducts),

    "Unexpected Products": len(UnexpectedProducts),

    "Invalid JSON Lines": len(InvalidJsonLines),

    "Missing Required Fields": len(MissingFields),

    "Invalid Embedding Dimensions": len(InvalidDimensions),

    "Invalid Embedding Values": len(InvalidEmbeddingValues),

    "Invalid Model Names": len(InvalidModelNames),

    "Invalid Task Prefixes": len(InvalidTaskPrefixes),

    "Invalid Text Hashes": len(InvalidTextHashes),

    "Failed Products": FailedProductCount

}


print("\n" + "-" * 65)
print("VALIDATION RESULTS")
print("-" * 65)

for ValidationName, ValidationCount in ValidationResults.items():

    print(f"{ValidationName:<35}: {ValidationCount}")


# ============================================================
# STEP 8: FINAL VALIDATION STATUS
# ============================================================

ValidationPassed = all(
    Count == 0
    for Name, Count in ValidationResults.items()
    if Name not in [
        "Expected Products",
        "Persisted Embeddings",
        "Unique Persisted Products"
    ]
)

ValidationPassed = (
    ValidationPassed
    and len(EmbeddingRecords) == len(ExpectedProducts)
    and len(PersistedProductKeys) == len(ExpectedProductKeys)
)

print("\n" + "=" * 65)

if ValidationPassed:

    print("RESULT: ALL EMBEDDING PERSISTENCE VALIDATIONS PASSED")

else:

    print("RESULT: EMBEDDING PERSISTENCE VALIDATION FAILED")

print("=" * 65)