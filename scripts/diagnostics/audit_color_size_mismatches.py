import pandas as pd
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]

# ============================================================

# CONFIGURATION

# ============================================================

OutputFolder = ProjectRoot / Path("data/output")

InputFile = (
OutputFolder /
"CandidatePairs_MaterialVerification_V2.csv"
)

AuditFolder = (
OutputFolder /
"quality" /
"mismatch_audit"
)

AuditFolder.mkdir(parents=True, exist_ok=True)

# ============================================================

# READ CANDIDATE DATA

# ============================================================

if not InputFile.exists():
    raise FileNotFoundError(
    f"Input file not found: {InputFile.resolve()}"
    )

CandidateDf = pd.read_csv(
InputFile,
dtype=str,
keep_default_na=False
)

print("=" * 65)
print("COLOR AND SIZE MISMATCH AUDIT")
print("=" * 65)

print(f"\nTotal candidate pairs: {len(CandidateDf)}")

# ============================================================

# VALIDATE REQUIRED COLUMNS

# ============================================================

RequiredColumns = [
"CandidatePairID",
"VerifiedColorMatch",
"VerifiedSizeMatch"
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

# ============================================================

# ADD MISMATCH REASON

# ============================================================

def GetMismatchReason(Row):


    Reasons = []

    if Row["VerifiedColorMatch"] == "MISMATCH":
        Reasons.append("COLOR_MISMATCH")

    if Row["VerifiedSizeMatch"] == "MISMATCH":
        Reasons.append("SIZE_MISMATCH")

    return " + ".join(Reasons)


CandidateDf["MismatchReason"] = CandidateDf.apply(
GetMismatchReason,
axis=1
)

# ============================================================

# FILTER COLOR AND SIZE MISMATCHES

# ============================================================

ColorMismatchDf = CandidateDf[
CandidateDf["VerifiedColorMatch"] == "MISMATCH"
].copy()

SizeMismatchDf = CandidateDf[
CandidateDf["VerifiedSizeMatch"] == "MISMATCH"
].copy()

BothMismatchDf = CandidateDf[
(
CandidateDf["VerifiedColorMatch"] == "MISMATCH"
) &
(
CandidateDf["VerifiedSizeMatch"] == "MISMATCH"
)
].copy()

CombinedMismatchDf = CandidateDf[
CandidateDf["MismatchReason"] != ""
].copy()

# ============================================================

# SELECT RELEVANT COLUMNS

# ============================================================

Keywords = [
"candidatepairid",
"stylehaus",
"urbanthread",
"productname",
"brand",
"category",
"color",
"colour",
"size",
"material",
"verified",
"similarity",
"mismatchreason"
]

AuditColumns = [
Column
for Column in CandidateDf.columns
if any(
Keyword in Column.lower()
for Keyword in Keywords
)
]

# Always retain these columns if they exist.

PriorityColumns = [
"CandidatePairID",
"StyleHaus_ProductName",
"UrbanThread_ProductName",
"StyleHaus_Color",
"UrbanThread_Color",
"StyleHaus_Size",
"UrbanThread_Size",
"VerifiedColorMatch",
"VerifiedSizeMatch",
"MismatchReason"
]

AuditColumns = [
Column
for Column in PriorityColumns
if Column in CandidateDf.columns
] + [
Column
for Column in AuditColumns
if Column not in PriorityColumns
]

# ============================================================

# EXPORT AUDIT FILES

# ============================================================

ColorMismatchDf[AuditColumns].to_csv(
AuditFolder / "Color_Mismatch_Audit.csv",
index=False
)

SizeMismatchDf[AuditColumns].to_csv(
AuditFolder / "Size_Mismatch_Audit.csv",
index=False
)

BothMismatchDf[AuditColumns].to_csv(
AuditFolder / "Color_And_Size_Mismatch_Audit.csv",
index=False
)

CombinedMismatchDf[AuditColumns].to_csv(
AuditFolder / "Combined_Mismatch_Audit.csv",
index=False
)

# ============================================================

# SUMMARY

# ============================================================

print("\nMISMATCH AUDIT SUMMARY")
print("-" * 45)

print(f"Total candidate pairs         : {len(CandidateDf)}")

print(f"Color mismatches              : {len(ColorMismatchDf)}")

print(f"Size mismatches               : {len(SizeMismatchDf)}")

print(f"Both color and size mismatch  : {len(BothMismatchDf)}")

print(f"Unique mismatch pairs        : {len(CombinedMismatchDf)}")

# ============================================================

# EXPORT VALIDATION

# ============================================================

print("\nGENERATED AUDIT FILES")
print("-" * 45)

for FilePath in sorted(AuditFolder.glob("*.csv")):


    ExportedDf = pd.read_csv(FilePath)

    print(
        f"{FilePath.name}: "
        f"{len(ExportedDf)} records"
    )


print("\nAudit folder:")
print(AuditFolder.resolve())

print("\nAudit completed successfully.")