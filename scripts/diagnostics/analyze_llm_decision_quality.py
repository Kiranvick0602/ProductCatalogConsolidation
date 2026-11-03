import json
from pathlib import Path

import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]


# ==============================================================================
# CONFIGURATION
# ==============================================================================

DecisionFilePath = Path(
    "data/output/llm/Phi3_MatchDecisions.jsonl"
)

AttributeFilePath = Path(
    "data/output/CandidatePairs_MaterialVerification.csv"
)

OutputFolderPath = Path(
    "data/output/llm/quality"
)

OutputFolderPath.mkdir(
    parents=True,
    exist_ok=True
)

DecisionSummaryPath = OutputFolderPath / "LLM_DecisionSummary.csv"
PotentialFalseMatchesPath = OutputFolderPath / "LLM_PotentialFalseMatches.csv"
ReviewCandidatesPath = OutputFolderPath / "LLM_ReviewCandidates.csv"
DecisionQualityReportPath = OutputFolderPath / "LLM_DecisionQualityReport.csv"


# ==============================================================================
# LOAD INPUT FILES
# ==============================================================================

if not DecisionFilePath.exists():
    raise FileNotFoundError(
        f"LLM decisions file not found: {DecisionFilePath}"
    )

if not AttributeFilePath.exists():
    raise FileNotFoundError(
        f"Attribute verification file not found: {AttributeFilePath}"
    )

DecisionRecords = []

with open(
    DecisionFilePath,
    "r",
    encoding="utf-8"
) as DecisionFile:

    for LineNumber, Line in enumerate(DecisionFile, start=1):

        if not Line.strip():
            continue

        try:
            DecisionRecords.append(json.loads(Line))

        except json.JSONDecodeError as Error:
            raise ValueError(
                f"Invalid JSON at line {LineNumber} "
                f"in {DecisionFilePath}: {Error}"
            ) from Error

DecisionDf = pd.DataFrame(DecisionRecords)

AttributeDf = pd.read_csv(
    AttributeFilePath,
    dtype=str,
    keep_default_na=False
)


# ==============================================================================
# INPUT VALIDATION
# ==============================================================================

RequiredDecisionColumns = [
    "CandidatePairID",
    "LLMDecision",
    "IsMatch",
    "Confidence",
    "Reason",
    "ResponseValid",
    "ModelName",
    "AttemptCount"
]

RequiredAttributeColumns = [
    "CandidatePairID",
    "StyleHaus_ProductID",
    "UrbanThread_ProductID",
    "StyleHaus_ProductName",
    "UrbanThread_ProductName",
    "EmbeddingSimilarity",
    "ProductNameSimilarity",
    "VerifiedBrandMatch",
    "VerifiedProductNameMatch",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

MissingDecisionColumns = [
    Column
    for Column in RequiredDecisionColumns
    if Column not in DecisionDf.columns
]

MissingAttributeColumns = [
    Column
    for Column in RequiredAttributeColumns
    if Column not in AttributeDf.columns
]

if MissingDecisionColumns:
    raise ValueError(
        f"Missing columns in decisions file: {MissingDecisionColumns}"
    )

if MissingAttributeColumns:
    raise ValueError(
        f"Missing columns in attribute file: {MissingAttributeColumns}"
    )

if DecisionDf["CandidatePairID"].duplicated().any():
    DuplicateIDs = DecisionDf.loc[
        DecisionDf["CandidatePairID"].duplicated(keep=False),
        "CandidatePairID"
    ].tolist()

    raise ValueError(
        f"Duplicate CandidatePairID values in decisions file: {DuplicateIDs[:10]}"
    )

if AttributeDf["CandidatePairID"].duplicated().any():
    DuplicateIDs = AttributeDf.loc[
        AttributeDf["CandidatePairID"].duplicated(keep=False),
        "CandidatePairID"
    ].tolist()

    raise ValueError(
        f"Duplicate CandidatePairID values in attribute file: {DuplicateIDs[:10]}"
    )


# ==============================================================================
# JOIN DECISIONS WITH ATTRIBUTE VERIFICATION
# ==============================================================================

AnalysisDf = DecisionDf.merge(
    AttributeDf,
    on="CandidatePairID",
    how="outer",
    suffixes=("_LLM", "_Attribute"),
    indicator=True,
    validate="one_to_one"
)

AnalysisDf["DecisionRecordFound"] = (
    AnalysisDf["_merge"].isin(["both", "left_only"])
)

AnalysisDf["AttributeRecordFound"] = (
    AnalysisDf["_merge"].isin(["both", "right_only"])
)

MatchedDf = AnalysisDf[
    AnalysisDf["_merge"] == "both"
].copy()

MatchedDf.drop(
    columns=["_merge"],
    inplace=True
)


# ==============================================================================
# NORMALIZE DECISION AND VERIFICATION VALUES
# ==============================================================================

MatchedDf["LLMDecision"] = (
    MatchedDf["LLMDecision"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
)

MatchedDf["ResponseValid"] = (
    MatchedDf["ResponseValid"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map({"true": True, "false": False})
)

MatchedDf["ConfidenceNumeric"] = pd.to_numeric(
    MatchedDf["Confidence"],
    errors="coerce"
)

MatchedDf["EmbeddingSimilarityNumeric"] = pd.to_numeric(
    MatchedDf["EmbeddingSimilarity"],
    errors="coerce"
)

MatchedDf["ProductNameSimilarityNumeric"] = pd.to_numeric(
    MatchedDf["ProductNameSimilarity"],
    errors="coerce"
)

VerificationColumns = [
    "VerifiedBrandMatch",
    "VerifiedProductNameMatch",
    "VerifiedCategoryMatch",
    "VerifiedColorMatch",
    "VerifiedSizeMatch",
    "VerifiedMaterialMatch"
]

for Column in VerificationColumns:
    MatchedDf[Column] = (
        MatchedDf[Column]
        .fillna("UNKNOWN")
        .astype(str)
        .str.strip()
        .str.upper()
    )


# ==============================================================================
# DECISION QUALITY FLAGS
# ==============================================================================

# UNKNOWN means that the attribute verifier could not establish a result.
# It is not treated as a mismatch.
# Only an explicit MISMATCH is treated as a verified attribute conflict.

MatchedDf["VerifiedAttributeMismatchCount"] = (
    MatchedDf[VerificationColumns]
    .eq("MISMATCH")
    .sum(axis=1)
)

MatchedDf["VerifiedAttributeUnknownCount"] = (
    MatchedDf[VerificationColumns]
    .eq("UNKNOWN")
    .sum(axis=1)
)

MatchedDf["HasVerifiedAttributeConflict"] = (
    MatchedDf["VerifiedAttributeMismatchCount"] > 0
)

MatchedDf["HasUnknownProductNameVerification"] = (
    MatchedDf["VerifiedProductNameMatch"] == "UNKNOWN"
)

MatchedDf["HasUnknownCategoryVerification"] = (
    MatchedDf["VerifiedCategoryMatch"] == "UNKNOWN"
)

MatchedDf["HasUnknownColorVerification"] = (
    MatchedDf["VerifiedColorMatch"] == "UNKNOWN"
)

MatchedDf["HasUnknownSizeVerification"] = (
    MatchedDf["VerifiedSizeMatch"] == "UNKNOWN"
)

MatchedDf["HasUnknownMaterialVerification"] = (
    MatchedDf["VerifiedMaterialMatch"] == "UNKNOWN"
)

MatchedDf["DecisionQualityFlag"] = "NO_RULE_BASED_WARNING"

MatchedDf.loc[
    MatchedDf["HasVerifiedAttributeConflict"],
    "DecisionQualityFlag"
] = "POTENTIAL_FALSE_MATCH_ATTRIBUTE_CONFLICT"

MatchedDf.loc[
    (
        MatchedDf["LLMDecision"] == "MATCH"
    )
    & (
        MatchedDf["HasUnknownProductNameVerification"]
    )
    & (
        ~MatchedDf["HasVerifiedAttributeConflict"]
    ),
    "DecisionQualityFlag"
] = "MATCH_REQUIRES_PRODUCT_IDENTITY_REVIEW"

MatchedDf.loc[
    MatchedDf["LLMDecision"] == "REVIEW",
    "DecisionQualityFlag"
] = "MANUAL_REVIEW"

MatchedDf.loc[
    MatchedDf["LLMDecision"] == "NO_MATCH",
    "DecisionQualityFlag"
] = "NO_MATCH_DECISION"


# ==============================================================================
# 1. DECISION SUMMARY
# ==============================================================================

DecisionCounts = (
    MatchedDf["LLMDecision"]
    .value_counts(dropna=False)
    .to_dict()
)

ExpectedDecisions = ["MATCH", "NO_MATCH", "REVIEW"]

SummaryRows = []

for Decision in ExpectedDecisions:

    DecisionRecordsDf = MatchedDf[
        MatchedDf["LLMDecision"] == Decision
    ]

    ConfidenceValues = DecisionRecordsDf[
        "ConfidenceNumeric"
    ].dropna()

    SummaryRows.append({
        "LLMDecision": Decision,
        "RecordCount": len(DecisionRecordsDf),
        "Percentage": (
            round(
                len(DecisionRecordsDf) / len(MatchedDf) * 100,
                2
            )
            if len(MatchedDf) > 0
            else 0
        ),
        "ValidResponses": int(
            DecisionRecordsDf["ResponseValid"].eq(True).sum()
        ),
        "ConfidenceCount": len(ConfidenceValues),
        "ConfidenceMinimum": (
            round(ConfidenceValues.min(), 6)
            if not ConfidenceValues.empty else None
        ),
        "ConfidenceMean": (
            round(ConfidenceValues.mean(), 6)
            if not ConfidenceValues.empty else None
        ),
        "ConfidenceMedian": (
            round(ConfidenceValues.median(), 6)
            if not ConfidenceValues.empty else None
        ),
        "ConfidenceMaximum": (
            round(ConfidenceValues.max(), 6)
            if not ConfidenceValues.empty else None
        )
    })

DecisionSummaryDf = pd.DataFrame(SummaryRows)

DecisionSummaryDf.to_csv(
    DecisionSummaryPath,
    index=False
)


# ==============================================================================
# 2. POTENTIAL FALSE MATCHES
# ==============================================================================

# This output includes only MATCH decisions with an explicit MISMATCH
# from the attribute verification layer. UNKNOWN is not considered a conflict.

PotentialFalseMatchesDf = MatchedDf[
    (
        MatchedDf["LLMDecision"] == "MATCH"
    )
    & (
        MatchedDf["HasVerifiedAttributeConflict"]
    )
].copy()

PotentialFalseMatchesDf.to_csv(
    PotentialFalseMatchesPath,
    index=False
)


# ==============================================================================
# 3. REVIEW CANDIDATES
# ==============================================================================

ReviewCandidatesDf = MatchedDf[
    MatchedDf["LLMDecision"] == "REVIEW"
].copy()

ReviewCandidatesDf.to_csv(
    ReviewCandidatesPath,
    index=False
)


# ==============================================================================
# 4. DECISION QUALITY REPORT
# ==============================================================================

QualityRows = [
    {
        "Metric": "Decision Records",
        "Value": len(DecisionDf)
    },
    {
        "Metric": "Attribute Verification Records",
        "Value": len(AttributeDf)
    },
    {
        "Metric": "Successfully Joined Records",
        "Value": len(MatchedDf)
    },
    {
        "Metric": "Decision Records Without Attribute Record",
        "Value": int((AnalysisDf["_merge"] == "left_only").sum())
    },
    {
        "Metric": "Attribute Records Without Decision Record",
        "Value": int((AnalysisDf["_merge"] == "right_only").sum())
    },
    {
        "Metric": "Unique Candidate Pair IDs in Decisions",
        "Value": DecisionDf["CandidatePairID"].nunique()
    },
    {
        "Metric": "Unique Candidate Pair IDs in Attribute Data",
        "Value": AttributeDf["CandidatePairID"].nunique()
    },
    {
        "Metric": "Valid LLM Responses",
        "Value": int(MatchedDf["ResponseValid"].eq(True).sum())
    },
    {
        "Metric": "Invalid or Missing LLM Responses",
        "Value": int((MatchedDf["ResponseValid"] != True).sum())
    },
    {
        "Metric": "MATCH Decisions",
        "Value": int((MatchedDf["LLMDecision"] == "MATCH").sum())
    },
    {
        "Metric": "NO_MATCH Decisions",
        "Value": int((MatchedDf["LLMDecision"] == "NO_MATCH").sum())
    },
    {
        "Metric": "REVIEW Decisions",
        "Value": int((MatchedDf["LLMDecision"] == "REVIEW").sum())
    },
    {
        "Metric": "MATCH Decisions With Explicit Attribute Conflict",
        "Value": len(PotentialFalseMatchesDf)
    },
    {
        "Metric": "MATCH Decisions With UNKNOWN Product Name Verification",
        "Value": int(
            (
                (MatchedDf["LLMDecision"] == "MATCH")
                & MatchedDf["HasUnknownProductNameVerification"]
            ).sum()
        )
    },
    {
        "Metric": "REVIEW Candidates",
        "Value": len(ReviewCandidatesDf)
    },
    {
        "Metric": "Average Embedding Similarity",
        "Value": round(
            MatchedDf["EmbeddingSimilarityNumeric"].mean(),
            6
        )
    },
    {
        "Metric": "Average Product Name Similarity",
        "Value": round(
            MatchedDf["ProductNameSimilarityNumeric"].mean(),
            6
        )
    }
]

DecisionQualityReportDf = pd.DataFrame(QualityRows)

DecisionQualityReportDf.to_csv(
    DecisionQualityReportPath,
    index=False
)


# ==============================================================================
# DISPLAY SUMMARY
# ==============================================================================

print("=" * 75)
print("LLM DECISION QUALITY ANALYSIS")
print("=" * 75)

print(f"Decision Records: {len(DecisionDf)}")
print(f"Attribute Records: {len(AttributeDf)}")
print(f"Successfully Joined Records: {len(MatchedDf)}")

print("\nDECISION SUMMARY")
print("-" * 75)
print(DecisionSummaryDf.to_string(index=False))

print("\nQUALITY CHECKS")
print("-" * 75)
print(DecisionQualityReportDf.to_string(index=False))

print("\nPOTENTIAL FALSE MATCHES")
print("-" * 75)
print(f"Records: {len(PotentialFalseMatchesDf)}")

print("\nREVIEW CANDIDATES")
print("-" * 75)
print(f"Records: {len(ReviewCandidatesDf)}")

print("\nOUTPUT FILES")
print("-" * 75)
print(f"Decision Summary: {DecisionSummaryPath}")
print(f"Potential False Matches: {PotentialFalseMatchesPath}")
print(f"Review Candidates: {ReviewCandidatesPath}")
print(f"Decision Quality Report: {DecisionQualityReportPath}")

print("\nAnalysis completed.")