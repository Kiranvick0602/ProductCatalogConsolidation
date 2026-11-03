import subprocess
import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]
ScriptsDirectory = Path(__file__).resolve().parent
Scripts = [
    ScriptsDirectory / "verify_candidate_brands.py",
    ScriptsDirectory / "verify_candidate_product_names.py",
    ScriptsDirectory / "verify_candidate_categories.py",
    ScriptsDirectory / "verify_candidate_colors.py",
    ScriptsDirectory / "verify_candidate_sizes.py",
    ScriptsDirectory / "verify_candidate_materials.py",
]

print("Starting Phase 5.5 V2 attribute verification pipeline...")
for Script in Scripts:
    print(f"\n{'=' * 80}\nRunning: {Script.name}\n{'=' * 80}")
    subprocess.run([sys.executable, str(Script)], cwd=ProjectRoot, check=True)

print("\nAll six V2 attribute verification stages completed successfully.")
print("Next run: python scripts/matching/run_final_matching_decisions.py")
