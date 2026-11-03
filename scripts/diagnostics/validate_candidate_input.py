from pathlib import Path
import pandas as pd

# ==================================================
# CONFIGURATION
# ==================================================

ProjectDirectory = Path(__file__).resolve().parents[2]

CandidateFilePath = (
    ProjectDirectory
    / "data"
    / "input"
    / "CandidatePairs.csv"
)

# ==================================================
# STEP 1: CHECK FILE AVAILABILITY
# ==================================================

print("Checking candidate input file...")

if not CandidateFilePath.exists():
    raise FileNotFoundError(
        f"Candidate file not found: {CandidateFilePath}"
    )

print("CandidatePairs.csv found successfully.")

# ==================================================
# STEP 2: READ CSV
# ==================================================

CandidatePairsDf = pd.read_csv(
    CandidateFilePath,
    encoding="utf-8"
)

# ==================================================
# STEP 3: DISPLAY FILE INFORMATION
# ==================================================

print("\n========== FILE INFORMATION ==========")
print(f"File Name      : {CandidateFilePath.name}")
print(f"Total Records  : {CandidatePairsDf.shape[0]}")
print(f"Total Columns  : {CandidatePairsDf.shape[1]}")

# ==================================================
# STEP 4: DISPLAY COLUMN NAMES
# ==================================================

print("\n========== COLUMN NAMES ==========")
for ColumnName in CandidatePairsDf.columns:
    print(ColumnName)

# ==================================================
# STEP 5: DISPLAY SAMPLE RECORDS
# ==================================================

print("\n========== SAMPLE RECORDS ==========")
print(
    CandidatePairsDf.head(5).to_string(index=False)
)

# ==================================================
# STEP 6: DATAFRAME INFORMATION
# ==================================================

print("\n========== DATAFRAME INFORMATION ==========")
CandidatePairsDf.info()
print("\nCandidate input validation completed.")
