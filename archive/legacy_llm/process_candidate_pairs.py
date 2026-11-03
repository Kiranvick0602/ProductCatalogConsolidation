import json
import time
import pandas as pd

from pathlib import Path

from ai_matching.llm.phi3_client import CallPhi3


# ==============================================================================
# CONFIGURATION
# ==============================================================================

InputFilePath = Path(
    "data/output/CandidatePairs_MaterialVerification.csv"
)

OutputFolderPath = Path(
    "data/output/llm"
)

CheckpointFilePath = (
    OutputFolderPath / "Phi3_MatchDecisions.jsonl"
)

FailedFilePath = (
    OutputFolderPath / "Phi3_FailedCandidates.jsonl"
)

OUTPUT_FOLDER = OutputFolderPath

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# Delay between successful API requests.
REQUEST_DELAY_SECONDS = 1


# ==============================================================================
# LOAD CANDIDATE DATA
# ==============================================================================

CandidateDf = pd.read_csv(
    InputFilePath,
    dtype=str,
    keep_default_na=False
)

TotalCandidates = len(CandidateDf)

print("=" * 75)
print("PHI-3 BATCH PRODUCT MATCHING")
print("=" * 75)

print(f"Total Candidate Pairs: {TotalCandidates}")


# ==============================================================================
# LOAD EXISTING CHECKPOINTS
# ==============================================================================

ProcessedCandidates = {}

if CheckpointFilePath.exists():

    with open(
        CheckpointFilePath,
        "r",
        encoding="utf-8"
    ) as File:

        for Line in File:

            if not Line.strip():
                continue

            Record = json.loads(Line)

            CandidatePairID = Record["CandidatePairID"]

            # Only valid LLM responses should be considered completed.

            if Record.get("ResponseValid") is True:

                ProcessedCandidates[CandidatePairID] = Record


print(
    f"Previously Processed Candidates: "
    f"{len(ProcessedCandidates)}"
)


# ==============================================================================
# IDENTIFY PENDING CANDIDATES
# ==============================================================================

PendingCandidates = CandidateDf[
    ~CandidateDf["CandidatePairID"].isin(
        ProcessedCandidates.keys()
    )
]

print(
    f"Remaining Candidates: {len(PendingCandidates)}"
)


# ==============================================================================
# PROCESS CANDIDATE PAIRS
# ==============================================================================

SuccessCount = 0
FailureCount = 0
ReviewCount = 0

with open(
    CheckpointFilePath,
    "a",
    encoding="utf-8"
) as CheckpointFile, open(
    FailedFilePath,
    "a",
    encoding="utf-8"
) as FailedFile:

    for Index, (_, CandidateRow) in enumerate(
        PendingCandidates.iterrows(),
        start=1
    ):

        Candidate = CandidateRow.to_dict()

        CandidatePairID = Candidate["CandidatePairID"]

        print("\n" + "-" * 75)

        print(
            f"Processing {Index}/{len(PendingCandidates)}"
        )

        print(
            f"CandidatePairID: {CandidatePairID}"
        )

        print(
            f"StyleHaus: {Candidate['StyleHaus_ProductName']}"
        )

        print(
            f"UrbanThread: {Candidate['UrbanThread_ProductName']}"
        )

        try:

            # --------------------------------------------------------------
            # CALL PHI-3
            # --------------------------------------------------------------

            Result = CallPhi3(Candidate)
            # ==========================================================================
            # VALIDATE RESPONSE BEFORE CHECKPOINTING
            # ==========================================================================

            if not Result["ResponseValid"]:

                FailureRecord = {
                    "CandidatePairID": CandidatePairID,
                    "Error": "Invalid LLM response",
                    "RawResponse": Result.get("RawResponse"),
                    "ProcessedAt": pd.Timestamp.now(
                        "UTC"
                    ).isoformat()
                }

                FailedFile.write(
                    json.dumps(
                        FailureRecord,
                        ensure_ascii=False
                    ) + "\n"
                )

                FailedFile.flush()

                FailureCount += 1

                print(
                    "Invalid LLM response. Not checkpointed."
                )

                continue
            # --------------------------------------------------------------
            # BUILD OUTPUT RECORD
            # --------------------------------------------------------------

            OutputRecord = {
                "CandidatePairID": CandidatePairID,
                "StyleHaus_ProductID": Candidate[
                    "StyleHaus_ProductID"
                ],
                "UrbanThread_ProductID": Candidate[
                    "UrbanThread_ProductID"
                ],
                "LLMDecision": Result["LLMDecision"],
                "IsMatch": Result["IsMatch"],
                "Confidence": Result["Confidence"],
                "Reason": Result["Reason"],
                "ResponseValid": Result["ResponseValid"],
                "ModelName": Result["ModelName"],
                "AttemptCount": Result["AttemptCount"],
                "RawResponse": Result["RawResponse"],
                "ProcessedAt": pd.Timestamp.now(
                    "UTC"
                ).isoformat()
            }

            # --------------------------------------------------------------
            # SAVE CHECKPOINT IMMEDIATELY
            # --------------------------------------------------------------

            CheckpointFile.write(
                json.dumps(
                    OutputRecord,
                    ensure_ascii=False
                ) + "\n"
            )

            CheckpointFile.flush()

            ProcessedCandidates[
                CandidatePairID
            ] = OutputRecord

            SuccessCount += 1

            if Result["LLMDecision"] == "REVIEW":
                ReviewCount += 1

            # --------------------------------------------------------------
            # DISPLAY RESULT
            # --------------------------------------------------------------

            print(
                f"Decision: {Result['LLMDecision']}"
            )

            print(
                f"Confidence: {Result['Confidence']}"
            )

            print(
                f"Response Valid: {Result['ResponseValid']}"
            )

            print(
                f"Reason: {Result['Reason']}"
            )

        except Exception as Error:

            FailureRecord = {
                "CandidatePairID": CandidatePairID,
                "Error": str(Error),
                "ProcessedAt": pd.Timestamp.now(
                    "UTC"
                ).isoformat()
            }

            FailedFile.write(
                json.dumps(
                    FailureRecord,
                    ensure_ascii=False
                ) + "\n"
            )

            FailedFile.flush()

            FailureCount += 1

            print(
                f"ERROR: {Error}"
            )

        # --------------------------------------------------------------
        # REQUEST DELAY
        # --------------------------------------------------------------

        if Index < len(PendingCandidates):

            time.sleep(
                REQUEST_DELAY_SECONDS
            )


# ==============================================================================
# CLEANUP RESOLVED FAILURE RECORDS
# ==============================================================================

if FailedFilePath.exists():

    with open(
        FailedFilePath,
        "r",
        encoding="utf-8"
    ) as FailedFile:

        FailureRecords = [
            json.loads(Line)
            for Line in FailedFile
            if Line.strip()
        ]

    RemainingFailures = [
        Record
        for Record in FailureRecords
        if Record["CandidatePairID"] not in ProcessedCandidates
    ]

    with open(
        FailedFilePath,
        "w",
        encoding="utf-8"
    ) as FailedFile:

        for Record in RemainingFailures:

            FailedFile.write(
                json.dumps(
                    Record,
                    ensure_ascii=False
                ) + "\\n"
            )

    print("\\nFailure File Cleanup:")
    print(f"Previous Failure Records: {len(FailureRecords)}")
    print(
        "Resolved Failure Records Removed: "
        f"{len(FailureRecords) - len(RemainingFailures)}"
    )
    print(f"Remaining Unresolved Failures: {len(RemainingFailures)}")


# ==============================================================================
# FINAL SUMMARY
# ==============================================================================

print("\n")
print("=" * 75)
print("PHI-3 BATCH PROCESSING SUMMARY")
print("=" * 75)

print(f"Total Candidates: {TotalCandidates}")

print(
    f"Previously Processed: "
    f"{TotalCandidates - len(PendingCandidates)}"
)

print(f"Newly Processed: {SuccessCount}")

print(f"Failed Requests: {FailureCount}")

print(f"Review Decisions: {ReviewCount}")

print(
    f"Total Checkpoint Records: "
    f"{len(ProcessedCandidates)}"
)

print("\nOutput Files:")

print(f"Checkpoint: {CheckpointFilePath}")

print(f"Failures: {FailedFilePath}")

print("\nBatch processing completed.")