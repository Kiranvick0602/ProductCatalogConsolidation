import pandas as pd
from pathlib import Path
from ai_matching.matching.decision_rules import EvaluateMatchDecision

ProjectRoot = Path(__file__).resolve().parent
InputFile = ProjectRoot / "data" / "output" / "CandidatePairs_MaterialVerification_V2.csv"
OutputFile = ProjectRoot / "data" / "output" / "CandidatePairs_RuleBasedDecisions_V2.csv"
EXPECTED_CANDIDATE_COUNT = 185

CandidateDf = pd.read_csv(InputFile, dtype=str, keep_default_na=False)
RequiredColumns = [
    "CandidatePairID", "VerifiedBrandMatch", "VerifiedProductNameMatch",
    "VerifiedCategoryMatch", "VerifiedColorMatch", "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]
MissingColumns = [Column for Column in RequiredColumns if Column not in CandidateDf.columns]
if MissingColumns:
    raise ValueError(f"Missing required columns: {MissingColumns}")
if len(CandidateDf) != EXPECTED_CANDIDATE_COUNT:
    raise ValueError(f"Expected {EXPECTED_CANDIDATE_COUNT} candidates; found {len(CandidateDf)}")
if CandidateDf["CandidatePairID"].eq("").any() or CandidateDf["CandidatePairID"].duplicated().any():
    raise ValueError("CandidatePairID is blank or duplicated.")

DecisionDf = pd.DataFrame(
    [EvaluateMatchDecision(Row) for Row in CandidateDf.to_dict(orient="records")]
)
FinalDf = pd.concat([CandidateDf.reset_index(drop=True), DecisionDf], axis=1)
FinalDf.to_csv(OutputFile, index=False, encoding="utf-8-sig")

print("RULE-BASED DECISION SUMMARY V2")
print(FinalDf["RuleBasedDecision"].value_counts(dropna=False).to_string())
print(f"Total candidates: {len(FinalDf)}")
print(f"Unique CandidatePairIDs: {FinalDf['CandidatePairID'].nunique()}")
print(f"Saved: {OutputFile}")
