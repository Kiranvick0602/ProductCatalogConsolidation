import json
import time
import math
import hashlib

from pathlib import Path

import pandas as pd
import requests

from ai_matching.config.settings import (
    LM_STUDIO_EMBEDDINGS_ENDPOINT,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_TASK_PREFIX,
    EMBEDDING_TIMEOUT
)


# ============================================================
# CONFIGURATION
# ============================================================

ProjectDirectory = Path(__file__).resolve().parents[2]

InputFilePath = (
    ProjectDirectory
    / "data"
    / "embeddings"
    / "UniqueProducts.csv"
)

OutputDirectory = (
    ProjectDirectory
    / "data"
    / "embeddings"
)

CheckpointFilePath = (
    OutputDirectory
    / "ProductEmbeddings.jsonl"
)

FailedProductsFilePath = (
    OutputDirectory
    / "FailedProducts.jsonl"
)

# Retry configuration
MAX_RETRIES = 3

RETRY_DELAY_SECONDS = 2

# Expected embedding dimension from our successful test
EXPECTED_EMBEDDING_DIMENSION = 768


# ============================================================
# HELPER FUNCTION: GENERATE TEXT HASH
# ============================================================

def GenerateTextHash(Text):

    return hashlib.sha256(
        Text.encode("utf-8")
    ).hexdigest()


# ============================================================
# HELPER FUNCTION: LOAD EXISTING CHECKPOINTS
# ============================================================

def LoadExistingEmbeddings():

    ExistingEmbeddings = {}

    if not CheckpointFilePath.exists():

        return ExistingEmbeddings

    print("\nLoading existing embedding checkpoints...")

    with open(
        CheckpointFilePath,
        "r",
        encoding="utf-8"
    ) as File:

        for LineNumber, Line in enumerate(File, start=1):

            if not Line.strip():
                continue

            try:

                Record = json.loads(Line)

                ProductKey = (
                    Record["Source"],
                    Record["ProductID"]
                )

                ExistingEmbeddings[ProductKey] = Record

            except (json.JSONDecodeError, KeyError) as Error:

                print(
                    f"Warning: Invalid checkpoint at line "
                    f"{LineNumber}: {Error}"
                )

    print(
        f"Existing checkpoints loaded: "
        f"{len(ExistingEmbeddings)}"
    )

    return ExistingEmbeddings


# ============================================================
# HELPER FUNCTION: SAVE EMBEDDING CHECKPOINT
# ============================================================

def SaveEmbeddingCheckpoint(EmbeddingRecord):

    with open(
        CheckpointFilePath,
        "a",
        encoding="utf-8"
    ) as File:

        File.write(
            json.dumps(
                EmbeddingRecord,
                ensure_ascii=False,
                allow_nan=False
            ) + "\n"
        )

        File.flush()


# ============================================================
# HELPER FUNCTION: SAVE FAILED PRODUCT
# ============================================================

def SaveFailedProduct(
    Product,
    ErrorMessage
):

    FailedRecord = {

        "Source": Product["Source"],

        "ProductID": Product["ProductID"],

        "Error": ErrorMessage,

        "Timestamp": pd.Timestamp.utcnow().isoformat()

    }

    with open(
        FailedProductsFilePath,
        "a",
        encoding="utf-8"
    ) as File:

        File.write(
            json.dumps(
                FailedRecord,
                ensure_ascii=False
            ) + "\n"
        )


# ============================================================
# HELPER FUNCTION: VALIDATE EMBEDDING
# ============================================================

def ValidateEmbedding(EmbeddingVector):

    if not isinstance(EmbeddingVector, list):

        raise ValueError(
            "Embedding response is not a list."
        )

    if len(EmbeddingVector) != EXPECTED_EMBEDDING_DIMENSION:

        raise ValueError(
            f"Unexpected embedding dimension: "
            f"{len(EmbeddingVector)}"
        )

    if not all(
        isinstance(Value, (int, float))
        and math.isfinite(Value)
        for Value in EmbeddingVector
    ):

        raise ValueError(
            "Embedding contains invalid numerical values."
        )


# ============================================================
# HELPER FUNCTION: GENERATE SINGLE EMBEDDING
# ============================================================

def GenerateEmbedding(
    Session,
    ProductText
):

    EmbeddingInput = (
        EMBEDDING_TASK_PREFIX + ProductText
    )

    Payload = {

        "model": EMBEDDING_MODEL_NAME,

        "input": EmbeddingInput

    }

    for Attempt in range(1, MAX_RETRIES + 1):

        try:

            Response = Session.post(

                LM_STUDIO_EMBEDDINGS_ENDPOINT,

                json=Payload,

                timeout=EMBEDDING_TIMEOUT

            )

            Response.raise_for_status()

            ResponseData = Response.json()

            EmbeddingVector = (
                ResponseData["data"][0]["embedding"]
            )

            ValidateEmbedding(EmbeddingVector)

            return EmbeddingVector

        except (
            requests.exceptions.RequestException,
            KeyError,
            IndexError,
            ValueError
        ) as Error:

            print(
                f"\nAttempt {Attempt}/{MAX_RETRIES} failed: "
                f"{Error}"
            )

            if Attempt < MAX_RETRIES:

                Delay = (
                    RETRY_DELAY_SECONDS * (2 ** (Attempt - 1))
                )

                print(
                    f"Retrying after {Delay} seconds..."
                )

                time.sleep(Delay)

            else:

                raise


# ============================================================
# MAIN PROCESS
# ============================================================

def GenerateProductEmbeddings():

    print("=" * 70)

    print("NOMIC PRODUCT EMBEDDING GENERATION")

    print("=" * 70)

    # --------------------------------------------------------
    # STEP 1: CHECK INPUT FILE
    # --------------------------------------------------------

    if not InputFilePath.exists():

        raise FileNotFoundError(
            f"Input file not found: {InputFilePath}"
        )

    OutputDirectory.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # STEP 2: READ UNIQUE PRODUCTS
    # --------------------------------------------------------

    UniqueProductsDf = pd.read_csv(
        InputFilePath,
        encoding="utf-8",
        dtype=str
    )

    RequiredColumns = [
        "Source",
        "ProductID",
        "CanonicalText"
    ]

    MissingColumns = [
        Column
        for Column in RequiredColumns
        if Column not in UniqueProductsDf.columns
    ]

    if MissingColumns:

        raise ValueError(
            f"Missing input columns: {MissingColumns}"
        )

    if UniqueProductsDf[RequiredColumns].isnull().any().any():

        raise ValueError(
            "Input contains null source, product ID or canonical text."
        )

    print(
        f"\nTotal Unique Products: {len(UniqueProductsDf)}"
    )

    # --------------------------------------------------------
    # STEP 3: LOAD EXISTING CHECKPOINTS
    # --------------------------------------------------------

    ExistingEmbeddings = LoadExistingEmbeddings()

    # --------------------------------------------------------
    # STEP 4: INITIALIZE HTTP SESSION
    # --------------------------------------------------------

    Session = requests.Session()

    Session.headers.update({

        "Content-Type": "application/json"

    })

    # --------------------------------------------------------
    # STEP 5: PROCESS PRODUCTS
    # --------------------------------------------------------

    GeneratedCount = 0

    SkippedCount = 0

    FailedCount = 0

    TotalProducts = len(UniqueProductsDf)

    print("\nStarting embedding generation...\n")

    for Index, Product in UniqueProductsDf.iterrows():

        Source = Product["Source"].strip()

        ProductID = Product["ProductID"].strip()

        CanonicalText = Product["CanonicalText"].strip()

        ProductKey = (
            Source,
            ProductID
        )

        TextHash = GenerateTextHash(
            CanonicalText
        )

        CurrentPosition = Index + 1

        # ----------------------------------------------------
        # CHECK EXISTING EMBEDDING
        # ----------------------------------------------------

        ExistingRecord = ExistingEmbeddings.get(
            ProductKey
        )

        if ExistingRecord:

            if ExistingRecord.get("TextHash") == TextHash:

                print(
                    f"[{CurrentPosition}/{TotalProducts}] "
                    f"SKIPPED | {Source} | {ProductID}"
                )

                SkippedCount += 1

                continue

            else:

                print(
                    f"\nCanonical text changed for "
                    f"{Source} | {ProductID}"
                )

                print(
                    "Generating a refreshed embedding."
                )

        # ----------------------------------------------------
        # GENERATE EMBEDDING
        # ----------------------------------------------------

        try:

            EmbeddingVector = GenerateEmbedding(
                Session,
                CanonicalText
            )

            EmbeddingRecord = {

                "Source": Source,

                "ProductID": ProductID,

                "TextHash": TextHash,

                "ModelName": EMBEDDING_MODEL_NAME,

                "TaskPrefix": EMBEDDING_TASK_PREFIX,

                "EmbeddingDimension": len(EmbeddingVector),

                "Embedding": EmbeddingVector,

                "GeneratedAt": pd.Timestamp.utcnow().isoformat()

            }

            # Save immediately after successful generation
            SaveEmbeddingCheckpoint(
                EmbeddingRecord
            )

            ExistingEmbeddings[ProductKey] = EmbeddingRecord

            GeneratedCount += 1

            print(

                f"[{CurrentPosition}/{TotalProducts}] "

                f"SUCCESS | {Source} | {ProductID}"

            )

        except Exception as Error:

            FailedCount += 1

            print(

                f"[{CurrentPosition}/{TotalProducts}] "

                f"FAILED | {Source} | {ProductID}"

            )

            SaveFailedProduct(
                Product,
                str(Error)
            )

    Session.close()

    # --------------------------------------------------------
    # STEP 6: FINAL SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print("EMBEDDING GENERATION SUMMARY")

    print("=" * 70)

    print(
        f"Total Unique Products : {TotalProducts}"
    )

    print(
        f"New Embeddings        : {GeneratedCount}"
    )

    print(
        f"Skipped Existing      : {SkippedCount}"
    )

    print(
        f"Failed Products       : {FailedCount}"
    )

    print(
        f"Checkpoint File       : {CheckpointFilePath}"
    )

    print("=" * 70)

    if FailedCount == 0:

        print(
            "\nEmbedding generation completed successfully."
        )

    else:

        print(
            "\nEmbedding generation completed with failures."
        )

        print(
            "Run the script again to retry failed products."
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    GenerateProductEmbeddings()