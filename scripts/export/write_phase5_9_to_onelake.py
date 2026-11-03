r"""
Phase 5.9 - Export final product matching datasets to OneLake Files.

Run from the project root:
    python scripts/export/write_phase5_9_to_onelake.py --onelake-files-path "C:\...\ProductCatalogLakehouse.Lakehouse\Files"

Inputs:
    data/output/CandidatePairs_FinalMatchingDecisions_V2.csv
    data/output/quality/phi3_validation/CandidatePairs_Phi3Validation.csv

Outputs:
    <OneLake Files path>/AI_Exchange/Output/Phase5_9/
        FinalMatchingDecisions.parquet
        Phi3ValidationResults.parquet
        FinalMatchingSummary.parquet
        manifest.json

This script exports files only. It does not create or modify Delta tables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINAL_DECISIONS_PATH = (
    PROJECT_ROOT / "data" / "output" / "CandidatePairs_FinalMatchingDecisions_V2.csv"
)
PHI3_RESULTS_PATH = (
    PROJECT_ROOT
    / "data" / "output"
    / "quality" / "phi3_validation"
    / "CandidatePairs_Phi3Validation.csv"
)

OUTPUT_RELATIVE_PATH = Path("AI_Exchange") / "Output" / "Phase5_9"

EXPECTED_DECISION_COUNTS = {
    "NO_MATCH": 155,
    "MATCH": 22,
    "REVIEW": 8,
}


def sha256_file(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_inputs(final_df: pd.DataFrame, phi3_df: pd.DataFrame) -> None:
    required_final = {
        "CandidatePairID",
        "FinalMatchDecision",
        "FinalMatchDecision_V2",
        "FinalDecisionReason_V2",
    }
    required_phi3 = {
        "CandidatePairID",
        "Phi3ValidationDecision",
        "Phi3Confidence",
        "Phi3Reason",
        "Phi3ResponseValid",
        "Phi3ModelName",
        "Phi3AttemptCount",
        "Phi3ProcessedAt",
    }

    missing_final = required_final - set(final_df.columns)
    missing_phi3 = required_phi3 - set(phi3_df.columns)

    if missing_final:
        raise ValueError(f"Final decisions file is missing columns: {sorted(missing_final)}")
    if missing_phi3:
        raise ValueError(f"Phi-3 results file is missing columns: {sorted(missing_phi3)}")

    if len(final_df) != 185:
        raise ValueError(f"Expected 185 candidate pairs; found {len(final_df)}.")
    if final_df["CandidatePairID"].isna().any() or final_df["CandidatePairID"].duplicated().any():
        raise ValueError("CandidatePairID must be populated and unique in final decisions.")

    if not final_df["FinalMatchDecision"].astype(str).equals(
        final_df["FinalMatchDecision_V2"].astype(str)
    ):
        raise ValueError("V2 decisions differ from original deterministic decisions.")

    actual_counts = (
        final_df["FinalMatchDecision_V2"].astype(str).str.upper().value_counts().to_dict()
    )
    if actual_counts != EXPECTED_DECISION_COUNTS:
        raise ValueError(
            f"Unexpected final decision counts. Expected {EXPECTED_DECISION_COUNTS}; "
            f"found {actual_counts}."
        )

    if len(phi3_df) != 8:
        raise ValueError(f"Expected 8 Phi-3 validation records; found {len(phi3_df)}.")
    if phi3_df["CandidatePairID"].isna().any() or phi3_df["CandidatePairID"].duplicated().any():
        raise ValueError("CandidatePairID must be populated and unique in Phi-3 results.")

    final_review_ids = set(
        final_df.loc[
            final_df["FinalMatchDecision_V2"].astype(str).str.upper().eq("REVIEW"),
            "CandidatePairID",
        ].astype(str)
    )
    phi3_ids = set(phi3_df["CandidatePairID"].astype(str))
    if final_review_ids != phi3_ids:
        raise ValueError(
            "Phi-3 CandidatePairID values do not exactly match the 8 final REVIEW records."
        )

    if not phi3_df["OriginalFinalMatchDecision"].astype(str).str.upper().eq("REVIEW").all():
        raise ValueError("Phi-3 file contains records not originally classified as REVIEW.")


def build_summary(final_df: pd.DataFrame, phi3_df: pd.DataFrame) -> pd.DataFrame:
    final_counts = (
        final_df["FinalMatchDecision_V2"].astype(str).str.upper().value_counts().to_dict()
    )
    phi3_counts = (
        phi3_df["Phi3ValidationDecision"].astype(str).str.upper().value_counts().to_dict()
    )

    summary_rows = [
        {"Metric": "TotalCandidatePairs", "Value": int(len(final_df))},
        {"Metric": "FinalMATCH", "Value": int(final_counts.get("MATCH", 0))},
        {"Metric": "FinalNO_MATCH", "Value": int(final_counts.get("NO_MATCH", 0))},
        {"Metric": "FinalREVIEW", "Value": int(final_counts.get("REVIEW", 0))},
        {"Metric": "Phi3ValidatedPairs", "Value": int(len(phi3_df))},
        {"Metric": "Phi3SuggestedMATCH", "Value": int(phi3_counts.get("MATCH", 0))},
        {"Metric": "Phi3SuggestedNO_MATCH", "Value": int(phi3_counts.get("NO_MATCH", 0))},
        {"Metric": "Phi3SuggestedREVIEW", "Value": int(phi3_counts.get("REVIEW", 0))},
        {"Metric": "Phi3SuggestionsAccepted", "Value": 0},
        {"Metric": "OriginalDecisionsPreserved", "Value": True},
    ]
    summary_df = pd.DataFrame(summary_rows)

    # Store all metric values as strings to ensure a consistent Parquet schema.
    summary_df["Value"] = summary_df["Value"].astype(str)

    return summary_df


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and export Phase 5.9 Parquet deliverables to OneLake Files."
    )
    parser.add_argument(
        "--onelake-files-path",
        required=True,
        help="Local OneLake-synced path to ProductCatalogLakehouse.Lakehouse\\Files.",
    )
    args = parser.parse_args()

    onelake_files_path = Path(args.onelake_files_path).expanduser()
    if not onelake_files_path.exists() or not onelake_files_path.is_dir():
        raise FileNotFoundError(
            "The OneLake Files path does not exist or is not a directory: "
            f"{onelake_files_path}"
        )

    if not FINAL_DECISIONS_PATH.exists():
        raise FileNotFoundError(f"Final decisions input not found: {FINAL_DECISIONS_PATH}")
    if not PHI3_RESULTS_PATH.exists():
        raise FileNotFoundError(f"Phi-3 validation input not found: {PHI3_RESULTS_PATH}")

    try:
        import pyarrow  # noqa: F401
    except ImportError as error:
        raise RuntimeError(
            "Parquet export requires pyarrow. Install it in the active .venv with: "
            "python -m pip install pyarrow"
        ) from error

    print("Reading Phase 5.8 final decisions...")
    final_df = pd.read_csv(FINAL_DECISIONS_PATH)
    print("Reading Phase 5.7 Phi-3 results...")
    phi3_df = pd.read_csv(PHI3_RESULTS_PATH)

    validate_inputs(final_df, phi3_df)
    summary_df = build_summary(final_df, phi3_df)

    output_dir = onelake_files_path / OUTPUT_RELATIVE_PATH
    output_dir.mkdir(parents=True, exist_ok=True)

    datasets = {
        "FinalMatchingDecisions": final_df,
        "Phi3ValidationResults": phi3_df,
        "FinalMatchingSummary": summary_df,
    }

    output_files: dict[str, Path] = {}
    for dataset_name, dataframe in datasets.items():
        output_path = output_dir / f"{dataset_name}.parquet"
        dataframe.to_parquet(output_path, index=False, engine="pyarrow", compression="snappy")
        # Read-after-write verification.
        readback_df = pd.read_parquet(output_path, engine="pyarrow")
        if len(readback_df) != len(dataframe):
            raise AssertionError(
                f"Read-back row count mismatch for {dataset_name}: "
                f"expected {len(dataframe)}, found {len(readback_df)}."
            )
        output_files[dataset_name] = output_path
        print(f"Written and verified: {output_path} ({len(readback_df)} rows)")

    manifest = {
        "Phase": "5.9",
        "Project": "Product Catalog Consolidation",
        "Workspace": "StyleHaus_UrbanThread",
        "Lakehouse": "ProductCatalogLakehouse",
        "CreatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "Format": "Parquet",
        "Compression": "snappy",
        "CandidatePairCount": int(len(final_df)),
        "Phi3ValidationCount": int(len(phi3_df)),
        "FinalDecisionCounts": {
            key: int(value)
            for key, value in final_df["FinalMatchDecision_V2"]
            .astype(str).str.upper().value_counts().to_dict().items()
        },
        "Phi3DecisionCounts": {
            key: int(value)
            for key, value in phi3_df["Phi3ValidationDecision"]
            .astype(str).str.upper().value_counts().to_dict().items()
        },
        "OriginalDeterministicDecisionsPreserved": True,
        "Files": {
            name: {
                "FileName": path.name,
                "Rows": int(len(datasets[name])),
                "SizeBytes": int(path.stat().st_size),
                "SHA256": sha256_file(path),
            }
            for name, path in output_files.items()
        },
    }

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nPhase 5.9 export completed successfully.")
    print(f"Output directory: {output_dir}")
    print(f"Manifest: {manifest_path}")
    print("Final decisions: 185 rows (155 NO_MATCH, 22 MATCH, 8 REVIEW)")
    print("Phi-3 validation: 8 rows")
    print("All Parquet files passed read-after-write verification.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exception:
        print(f"PHASE 5.9 FAILED: {exception}", file=sys.stderr)
        raise
