"""
Phase 5.8 - Consolidate deterministic final decisions with Phi-3 evidence.

Inputs:
  data/output/CandidatePairs_FinalMatchingDecisions.csv
  data/output/quality/phi3_validation/CandidatePairs_Phi3Validation.csv

Outputs:
  data/output/CandidatePairs_FinalMatchingDecisions_V2.csv
  data/output/quality/final_matching/Phase5_8_FinalDecision_Summary.csv

Phi-3 is supporting evidence only. It never overrides deterministic decisions.
"""
from pathlib import Path
import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]
FinalInputPath = ProjectRoot / "data" / "output" / "CandidatePairs_FinalMatchingDecisions.csv"
PhiInputPath = ProjectRoot / "data" / "output" / "quality" / "phi3_validation" / "CandidatePairs_Phi3Validation.csv"
OutputPath = ProjectRoot / "data" / "output" / "CandidatePairs_FinalMatchingDecisions_V2.csv"
SummaryPath = ProjectRoot / "data" / "output" / "quality" / "final_matching" / "Phase5_8_FinalDecision_Summary.csv"

def main():
    FinalDf = pd.read_csv(FinalInputPath)
    PhiDf = pd.read_csv(PhiInputPath)

    RequiredFinal = {"CandidatePairID", "FinalMatchDecision", "DecisionReason"}
    RequiredPhi = {
        "CandidatePairID", "OriginalFinalMatchDecision",
        "Phi3ValidationDecision", "Phi3Confidence", "Phi3Reason",
        "Phi3ResponseValid", "Phi3ModelName", "Phi3AttemptCount",
        "Phi3ProcessedAt"
    }
    MissingFinal = RequiredFinal - set(FinalDf.columns)
    MissingPhi = RequiredPhi - set(PhiDf.columns)
    if MissingFinal or MissingPhi:
        raise ValueError(f"Missing columns. Final={MissingFinal}; Phi3={MissingPhi}")

    if FinalDf["CandidatePairID"].duplicated().any():
        raise ValueError("CandidatePairID is not unique in deterministic decisions.")
    if PhiDf["CandidatePairID"].duplicated().any():
        raise ValueError("CandidatePairID is not unique in Phi-3 results.")
    if not PhiDf["OriginalFinalMatchDecision"].astype(str).str.upper().eq("REVIEW").all():
        raise ValueError("Phi-3 file contains a record that was not originally REVIEW.")
    if not set(PhiDf["CandidatePairID"]).issubset(set(FinalDf["CandidatePairID"])):
        raise ValueError("Phi-3 file contains unknown CandidatePairID values.")

    PhiColumns = [
        "Phi3ValidationDecision", "Phi3Confidence", "Phi3Reason",
        "Phi3ResponseValid", "Phi3ModelName", "Phi3AttemptCount",
        "Phi3ProcessedAt"
    ]
    ResultDf = FinalDf.merge(
        PhiDf[["CandidatePairID"] + PhiColumns],
        on="CandidatePairID", how="left", validate="one_to_one"
    )

    # Conservative adjudication: LLM suggestions are not allowed to override
    # deterministic decisions. The seven MATCH suggestions have confidence 0.0
    # and the source critical attributes remain unresolved.
    ResultDf["FinalMatchDecision_V2"] = ResultDf["FinalMatchDecision"]
    ResultDf["FinalDecisionReason_V2"] = ResultDf["DecisionReason"]
    ResultDf["Phi3DecisionAccepted"] = False
    ResultDf["Phase5_8Adjudication"] = "NO_PHI3_RECOMMENDATION"

    IsReview = ResultDf["FinalMatchDecision"].astype(str).str.upper().eq("REVIEW")
    ResultDf.loc[IsReview, "Phase5_8Adjudication"] = "RETAIN_REVIEW_DETERMINISTIC_RULES"
    IsPhiMatch = IsReview & ResultDf["Phi3ValidationDecision"].astype(str).str.upper().eq("MATCH")
    IsPhiReview = IsReview & ResultDf["Phi3ValidationDecision"].astype(str).str.upper().eq("REVIEW")
    ResultDf.loc[IsPhiMatch, "Phase5_8Adjudication"] = (
        "PHI3_MATCH_NOT_ACCEPTED_UNRESOLVED_CRITICAL_ATTRIBUTES"
    )
    ResultDf.loc[IsPhiReview, "Phase5_8Adjudication"] = (
        "RETAIN_REVIEW_LLM_ALSO_UNRESOLVED"
    )

    if len(ResultDf) != len(FinalDf):
        raise AssertionError("Candidate row count changed during consolidation.")
    if not ResultDf["FinalMatchDecision_V2"].equals(ResultDf["FinalMatchDecision"]):
        raise AssertionError("Original deterministic decisions were changed.")
    if int(ResultDf["Phi3ValidationDecision"].notna().sum()) != len(PhiDf):
        raise AssertionError("Phi-3 evidence join did not match all rows.")

    OutputPath.parent.mkdir(parents=True, exist_ok=True)
    SummaryPath.parent.mkdir(parents=True, exist_ok=True)
    ResultDf.to_csv(OutputPath, index=False, encoding="utf-8-sig")

    Summary = pd.DataFrame([
        {"Metric": "TotalCandidatePairs", "Value": len(ResultDf)},
        {"Metric": "FinalMATCH", "Value": int(ResultDf["FinalMatchDecision_V2"].eq("MATCH").sum())},
        {"Metric": "FinalNO_MATCH", "Value": int(ResultDf["FinalMatchDecision_V2"].eq("NO_MATCH").sum())},
        {"Metric": "FinalREVIEW", "Value": int(ResultDf["FinalMatchDecision_V2"].eq("REVIEW").sum())},
        {"Metric": "Phi3ValidatedPairs", "Value": int(ResultDf["Phi3ValidationDecision"].notna().sum())},
        {"Metric": "Phi3SuggestedMATCH", "Value": int(ResultDf["Phi3ValidationDecision"].eq("MATCH").sum())},
        {"Metric": "Phi3SuggestedNO_MATCH", "Value": int(ResultDf["Phi3ValidationDecision"].eq("NO_MATCH").sum())},
        {"Metric": "Phi3SuggestedREVIEW", "Value": int(ResultDf["Phi3ValidationDecision"].eq("REVIEW").sum())},
        {"Metric": "Phi3SuggestionsAccepted", "Value": int(ResultDf["Phi3DecisionAccepted"].sum())},
        {"Metric": "OriginalDecisionsPreserved", "Value": True},
    ])
    Summary.to_csv(SummaryPath, index=False, encoding="utf-8-sig")

    print(f"Candidate pairs: {len(ResultDf)}")
    print("Final decision counts:")
    print(ResultDf["FinalMatchDecision_V2"].value_counts().to_string())
    print("\\nPhi-3 evidence counts:")
    print(ResultDf["Phi3ValidationDecision"].value_counts(dropna=True).to_string())
    print(f"\\nFinal output: {OutputPath}")
    print(f"Summary:      {SummaryPath}")
    print("Original deterministic decisions preserved.")

if __name__ == "__main__":
    main()
