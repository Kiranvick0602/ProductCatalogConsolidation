import json

from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]


# ==============================================================================
# CONFIGURATION
# ==============================================================================

CheckpointFilePath = Path(
    "data/output/llm/Phi3_MatchDecisions.jsonl"
)

TemporaryFilePath = Path(
    "data/output/llm/Phi3_MatchDecisions_Temp.jsonl"
)


# ==============================================================================
# CLEAN EXISTING CHECKPOINT
# ==============================================================================

ValidCount = 0
InvalidCount = 0


if CheckpointFilePath.exists():

    with open(
        CheckpointFilePath,
        "r",
        encoding="utf-8"
    ) as InputFile, open(
        TemporaryFilePath,
        "w",
        encoding="utf-8"
    ) as OutputFile:

        for Line in InputFile:

            if not Line.strip():
                continue

            Record = json.loads(Line)

            if Record.get("ResponseValid") is True:

                OutputFile.write(
                    json.dumps(
                        Record,
                        ensure_ascii=False
                    ) + "\n"
                )

                ValidCount += 1

            else:

                InvalidCount += 1

    TemporaryFilePath.replace(
        CheckpointFilePath
    )

else:

    print("Checkpoint file does not exist.")


# ==============================================================================
# DISPLAY SUMMARY
# ==============================================================================

print("=" * 60)
print("CHECKPOINT CLEANUP SUMMARY")
print("=" * 60)

print("Valid Records Retained:", ValidCount)

print("Invalid Records Removed:", InvalidCount)

print("Cleanup Completed.")