import pandas as pd
from pathlib import Path

from ai_matching.matching.decision_rules import EvaluateMatchDecision


# ==============================================================================
# CONFIGURATION
# ==============================================================================

InputFile = Path(
    "data/output/CandidatePairs_MaterialVerification.csv"
)

OutputFile = Path(
    "data/output/CandidatePairs_RuleBasedDecisions.csv"
)


# ==============================================================================
# STEP 1: LOAD ATTRIBUTE VERIFICATION DATA
# ==============================================================================

CandidateDf = pd.read_csv(InputFile)

print(f"Input Candidate Count: {len(CandidateDf)}")


# ==============================================================================
# STEP 2: VALIDATE INPUT DATA
# ==============================================================================

RequiredColumns = [
    "CandidatePairID",
    "VerifiedBrandMatch",
    "VerifiedProductNameMatch",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

MissingColumns = [
    Column
    for Column in RequiredColumns
    if Column not in CandidateDf.columns
]

if MissingColumns:
    raise ValueError(
        f"Missing required columns: {MissingColumns}"
    )

if CandidateDf["CandidatePairID"].isnull().any():
    raise ValueError("CandidatePairID contains NULL values.")

if CandidateDf["CandidatePairID"].duplicated().any():
    raise ValueError("Duplicate CandidatePairID values found.")


# ==============================================================================
# STEP 3: APPLY RULE-BASED DECISION LOGIC
# ==============================================================================

DecisionResults = []

for Candidate in CandidateDf.to_dict(orient="records"):

    Decision = EvaluateMatchDecision(Candidate)

    DecisionResults.append(Decision)


DecisionDf = pd.DataFrame(DecisionResults)


# ==============================================================================
# STEP 4: ADD DECISIONS TO ORIGINAL CANDIDATE DATA
# ==============================================================================

FinalDf = pd.concat(
    [
        CandidateDf.reset_index(drop=True),
        DecisionDf.reset_index(drop=True)
    ],
    axis=1
)


# ==============================================================================
# STEP 5: SAVE OUTPUT
# ==============================================================================

FinalDf.to_csv(
    OUTPUTFILE := OutputFile,
    index=False
)


# ==============================================================================
# STEP 6: DISPLAY DECISION SUMMARY
# ==============================================================================

print("\n" + "=" * 60)
print("RULE-BASED DECISION SUMMARY")
print("=" * 60)

print(
    FinalDf["RuleBasedDecision"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nTotal Candidates:", len(FinalDf))

print(
    "Unique CandidatePairIDs:",
    FinalDf["CandidatePairID"].nunique()
)

print("\nOutput File:", OutputFile)