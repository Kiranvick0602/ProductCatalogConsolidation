import sys
from pathlib import Path
import pandas as pd

ProjectDirectory = Path(__file__).resolve().parents[2]
if str(ProjectDirectory) not in sys.path:
    sys.path.insert(0, str(ProjectDirectory))

from ai_matching.utils.canonical_text import (
    BuildCanonicalProductText
)


# ============================================================
# CONFIGURATION
# ============================================================

InputFilePath = (
    ProjectDirectory
    / "data"
    / "input"
    / "CandidatePairs.csv"
)

OutputDirectory = (
    ProjectDirectory
    / "data"
    / "output"
)

OutputFilePath = (
    OutputDirectory
    / "CandidatePairs_CanonicalText.csv"
)


# ============================================================
# STEP 1: READ CANDIDATE PAIRS
# ============================================================

print("=" * 65)
print("CANONICAL PRODUCT TEXT GENERATION")
print("=" * 65)

CandidatePairsDf = pd.read_csv(
    InputFilePath,
    encoding="utf-8"
)

print(
    f"\nCandidate pairs loaded: {len(CandidatePairsDf)}"
)


# ============================================================
# STEP 2: GENERATE STYLEHAUS CANONICAL TEXT
# ============================================================

print("\nGenerating StyleHaus canonical text...")

CandidatePairsDf["StyleHaus_CanonicalText"] = (
    CandidatePairsDf.apply(
        lambda Record: BuildCanonicalProductText(
            Record,
            "StyleHaus"
        ),
        axis=1
    )
)


# ============================================================
# STEP 3: GENERATE URBANTHREAD CANONICAL TEXT
# ============================================================

print("Generating UrbanThread canonical text...")

CandidatePairsDf["UrbanThread_CanonicalText"] = (
    CandidatePairsDf.apply(
        lambda Record: BuildCanonicalProductText(
            Record,
            "UrbanThread"
        ),
        axis=1
    )
)


# ============================================================
# STEP 4: VALIDATE GENERATED TEXT
# ============================================================

print("\n========== CANONICAL TEXT VALIDATION ==========")

StyleHausEmptyCount = (
    CandidatePairsDf["StyleHaus_CanonicalText"]
    .str.strip()
    .eq("")
    .sum()
)

UrbanThreadEmptyCount = (
    CandidatePairsDf["UrbanThread_CanonicalText"]
    .str.strip()
    .eq("")
    .sum()
)

print(
    f"StyleHaus empty texts   : {StyleHausEmptyCount}"
)

print(
    f"UrbanThread empty texts : {UrbanThreadEmptyCount}"
)

print(
    f"Total StyleHaus texts   : "
    f"{len(CandidatePairsDf)}"
)

print(
    f"Total UrbanThread texts : "
    f"{len(CandidatePairsDf)}"
)


# ============================================================
# STEP 5: DISPLAY SAMPLE CANONICAL TEXT
# ============================================================

print("\n========== SAMPLE STYLEHAUS TEXT ==========")

print(
    CandidatePairsDf.loc[
        0,
        "StyleHaus_CanonicalText"
    ]
)

print("\n========== SAMPLE URBANTHREAD TEXT ==========")

print(
    CandidatePairsDf.loc[
        0,
        "UrbanThread_CanonicalText"
    ]
)


# ============================================================
# STEP 6: SAVE OUTPUT
# ============================================================

OutputDirectory.mkdir(
    parents=True,
    exist_ok=True
)

CandidatePairsDf.to_csv(
    OutputFilePath,
    index=False,
    encoding="utf-8"
)

print("\n========== OUTPUT INFORMATION ==========")
print(f"Output file: {OutputFilePath}")
print(f"Total columns: {CandidatePairsDf.shape[1]}")
print(f"Total records: {CandidatePairsDf.shape[0]}")
print("\nCanonical text generation completed.")
