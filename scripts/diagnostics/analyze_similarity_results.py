import pandas as pd

from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

ProjectDirectory = Path(__file__).resolve().parents[2]

InputPath = (
    ProjectDirectory
    / "data"
    / "output"
    / "CandidatePairs_EmbeddingSimilarity.csv"
)

OutputDirectory = (
    ProjectDirectory
    / "data"
    / "output"
)


# ============================================================
# LOAD DATA
# ============================================================

CandidatePairsDf = pd.read_csv(
    InputPath
)

CandidatePairsDf = CandidatePairsDf.sort_values(
    by="EmbeddingSimilarity",
    ascending=False
)


# ============================================================
# SELECT IMPORTANT COLUMNS
# ============================================================

AnalysisColumns = [
    "CandidatePairID",
    "StyleHaus_ProductID",
    "UrbanThread_ProductID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "StyleHaus_Category",
    "UrbanThread_Category",
    "StyleHaus_Color",
    "UrbanThread_Color",
    "StyleHaus_Size",
    "UrbanThread_Size",
    "StyleHaus_Material",
    "UrbanThread_Material",
    "EmbeddingSimilarity"
]

AnalysisDf = CandidatePairsDf[AnalysisColumns]


# ============================================================
# HIGHEST SIMILARITY
# ============================================================

print("\n" + "=" * 100)
print("TOP 10 HIGHEST SIMILARITY PAIRS")
print("=" * 100)

print(
    AnalysisDf.head(10).to_string(index=False)
)


# ============================================================
# LOWEST SIMILARITY
# ============================================================

print("\n" + "=" * 100)
print("TOP 10 LOWEST SIMILARITY PAIRS")
print("=" * 100)

print(
    AnalysisDf.tail(10).to_string(index=False)
)


# ============================================================
# SAVE ANALYSIS
# ============================================================

OutputPath = (
    OutputDirectory
    / "SimilarityAnalysis.csv"
)

AnalysisDf.to_csv(
    OutputPath,
    index=False
)

print("\nAnalysis file saved:")
print(OutputPath)