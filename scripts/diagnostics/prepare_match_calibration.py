import json
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# File paths
# --------------------------------------------------

ProjectRoot = Path(__file__).resolve().parents[2]

SimilarityFile = (
    ProjectRoot
    / "data"
    / "output"
    / "CandidatePairs_EmbeddingSimilarity.csv"
)

DecisionFile = (
    ProjectRoot
    / "data"
    / "output"
    / "llm"
    / "Phi3_MatchDecisions.jsonl"
)

OutputFile = (
    ProjectRoot
    / "data"
    / "output"
    / "llm"
    / "quality"
    / "MATCH_DecisionCalibration.csv"
)


# --------------------------------------------------
# Load candidate evidence
# --------------------------------------------------

CandidateDf = pd.read_csv(SimilarityFile)

DecisionRecords = []

with open(DecisionFile, "r", encoding="utf-8") as File:
    for Line in File:
        if Line.strip():
            DecisionRecords.append(json.loads(Line))


DecisionDf = pd.DataFrame(DecisionRecords)


# --------------------------------------------------
# Filter MATCH decisions
# --------------------------------------------------

MatchDf = DecisionDf[
    DecisionDf["LLMDecision"] == "MATCH"
].copy()


# --------------------------------------------------
# Join candidate evidence
# --------------------------------------------------

CalibrationDf = MatchDf.merge(
    CandidateDf,
    on="CandidatePairID",
    how="left",
    validate="one_to_one"
)


# --------------------------------------------------
# Select relevant columns
# --------------------------------------------------

ReviewColumns = [
    "CandidatePairID",
    "StyleHaus_ProductID",
    "UrbanThread_ProductID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "EmbeddingSimilarity",
    "ProductNameSimilarity",
    "CategoryMatch",
    "ColorMatch",
    "SizeMatch",
    "MaterialMatch",
    "DescriptionSimilarity",
    "PriceDifferencePct",
    "LLMDecision",
    "Confidence",
    "Reason"
]

CalibrationDf = CalibrationDf[
    [Column for Column in ReviewColumns
     if Column in CalibrationDf.columns]
]


# --------------------------------------------------
# Sort and export
# --------------------------------------------------

CalibrationDf = CalibrationDf.sort_values(
    by="EmbeddingSimilarity",
    ascending=False
)

CalibrationDf.to_csv(OutputFile, index=False)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("MATCH Decision Calibration Export")
print("---------------------------------")
print(f"LLM MATCH decisions : {len(MatchDf)}")
print(f"Joined records      : {len(CalibrationDf)}")
print(f"Output file         : {OutputFile}")