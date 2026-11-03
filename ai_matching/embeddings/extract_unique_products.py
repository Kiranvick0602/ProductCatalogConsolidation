from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

ProjectDirectory = Path(__file__).resolve().parents[2]

InputFilePath = (
    ProjectDirectory
    / "data"
    / "output"
    / "CandidatePairs_CanonicalText.csv"
)

OutputDirectory = (
    ProjectDirectory
    / "data"
    / "embeddings"
)

OutputFilePath = (
    OutputDirectory
    / "UniqueProducts.csv"
)


# ============================================================
# STEP 1: READ CANDIDATE PAIRS
# ============================================================

CandidatePairsDf = pd.read_csv(
    InputFilePath,
    encoding="utf-8"
)

print("=" * 65)
print("UNIQUE PRODUCT EXTRACTION")
print("=" * 65)

print(
    f"\nTotal Candidate Pairs: {len(CandidatePairsDf)}"
)


# ============================================================
# STEP 2: EXTRACT STYLEHAUS PRODUCTS
# ============================================================

StyleHausProductsDf = CandidatePairsDf[
    [
        "StyleHaus_ProductID",
        "StyleHaus_CanonicalText"
    ]
].copy()

StyleHausProductsDf.columns = [
    "ProductID",
    "CanonicalText"
]

StyleHausProductsDf["Source"] = "StyleHaus"


# ============================================================
# STEP 3: EXTRACT URBANTHREAD PRODUCTS
# ============================================================

UrbanThreadProductsDf = CandidatePairsDf[
    [
        "UrbanThread_ProductID",
        "UrbanThread_CanonicalText"
    ]
].copy()

UrbanThreadProductsDf.columns = [
    "ProductID",
    "CanonicalText"
]

UrbanThreadProductsDf["Source"] = "UrbanThread"


# ============================================================
# STEP 4: COMBINE BOTH SOURCES
# ============================================================

UniqueProductsDf = pd.concat(
    [
        StyleHausProductsDf,
        UrbanThreadProductsDf
    ],
    ignore_index=True
)

# Remove accidental whitespace around IDs and text.
UniqueProductsDf["ProductID"] = (
    UniqueProductsDf["ProductID"].astype(str).str.strip()
)

UniqueProductsDf["CanonicalText"] = (
    UniqueProductsDf["CanonicalText"].fillna("").str.strip()
)


# ============================================================
# STEP 5: VALIDATE PRODUCT IDs AND CANONICAL TEXT
# ============================================================

if UniqueProductsDf["ProductID"].eq("").any():

    raise ValueError("Empty product IDs found.")

if UniqueProductsDf["CanonicalText"].eq("").any():

    raise ValueError("Empty canonical product texts found.")


# A source product must always have the same canonical text.
ConflictingProductsDf = (
    UniqueProductsDf
    .groupby(["Source", "ProductID"])["CanonicalText"]
    .nunique()
    .reset_index(name="TextCount")
    .query("TextCount > 1")
)

if not ConflictingProductsDf.empty:

    raise ValueError(
        "Some products have conflicting canonical texts. "
        "Resolve these before generating embeddings."
    )


# ============================================================
# STEP 6: REMOVE DUPLICATE PRODUCTS
# ============================================================

UniqueProductsDf = UniqueProductsDf.drop_duplicates(
    subset=["Source", "ProductID"]
).reset_index(drop=True)


# ============================================================
# STEP 7: REORDER COLUMNS
# ============================================================

UniqueProductsDf = UniqueProductsDf[
    [
        "Source",
        "ProductID",
        "CanonicalText"
    ]
]


# ============================================================
# STEP 8: DISPLAY RESULTS
# ============================================================

StyleHausCount = (
    UniqueProductsDf["Source"] == "StyleHaus"
).sum()

UrbanThreadCount = (
    UniqueProductsDf["Source"] == "UrbanThread"
).sum()

print("\n========== UNIQUE PRODUCT COUNTS ==========")

print(f"StyleHaus Unique Products  : {StyleHausCount}")

print(f"UrbanThread Unique Products: {UrbanThreadCount}")

print(f"Total Unique Products      : {len(UniqueProductsDf)}")

print(
    f"Original Product References: "
    f"{len(CandidatePairsDf) * 2}"
)


# ============================================================
# STEP 9: SAVE UNIQUE PRODUCTS
# ============================================================

OutputDirectory.mkdir(
    parents=True,
    exist_ok=True
)

UniqueProductsDf.to_csv(
    OutputFilePath,
    index=False,
    encoding="utf-8"
)

print("\n========== OUTPUT ==========")

print(f"Output File: {OutputFilePath}")

print("\nUnique product extraction completed.")