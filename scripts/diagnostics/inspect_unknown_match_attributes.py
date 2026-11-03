from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]

InputFile = str(ProjectRoot / "data/output/CandidatePairs_RuleBasedDecisions.csv")

Df = pd.read_csv(InputFile)

# Load original Phi-3 decisions
LLMFile = str(ProjectRoot / "data/output/llm/Phi3_MatchDecisions.jsonl")

LLMDf = pd.read_json(LLMFile, lines=True)

# Select Phi-3 MATCH decisions
LLMMatches = LLMDf[
    LLMDf["LLMDecision"] == "MATCH"
]

# Join with attribute verification data
MatchDf = Df.merge(
    LLMMatches[
        ["CandidatePairID", "LLMDecision", "Confidence", "Reason"]
    ],
    on="CandidatePairID",
    how="inner"
)

# Select relevant product attributes
Columns = [
    "CandidatePairID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "StyleHaus_Color",
    "UrbanThread_Color",
    "StyleHaus_Size",
    "UrbanThread_Size",
    "StyleHaus_Material",
    "UrbanThread_Material",
    "VerifiedProductNameMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch",
    "LLMDecision",
    "Confidence"
]

ResultDf = MatchDf[Columns]

print("Phi-3 MATCH records:", len(ResultDf))

print("\nUNKNOWN attribute counts:")
for Column in [
    "VerifiedProductNameMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]:
    print(
        Column,
        ResultDf[Column].value_counts(dropna=False).to_dict()
    )

ResultDf.to_csv(
    "data/output/llm/UnknownMatchAttributeAnalysis.csv",
    index=False
)

print("\nOutput saved:")
print("data/output/llm/UnknownMatchAttributeAnalysis.csv")