# Phase 5.5 – V2 Attribute Verification Package

## What this package changes

- Uses the improved `attribute_verification.py` supplied for this project.
- Re-runs the six existing verification stages in their original cumulative order.
- Writes all verification outputs with `_V2` suffixes; original CSV outputs are not overwritten.
- Uses five mandatory identity attributes: Brand, Product Name, Category, Color, Size.
- Treats Material as supporting evidence only; a material mismatch alone does not force `NO_MATCH`.
- Adds a runner and a separate rule-based decision script.

## Copy the files

Copy the package contents into the project root `D:\Projects\ProductCatalogConsolidation`, preserving the folders. The files under `ai_matching\matching` should be copied into the existing `ai_matching\matching` folder. Back up the current `attribute_verification.py` and `decision_rules.py` before replacing them.

## Run from the VS Code terminal

Make sure the `.venv` interpreter is selected and active. From the project root:

```powershell
python run_attribute_verification_v2.py
```

This runs the six stages in order and creates:

1. `data/output/CandidatePairs_BrandVerification_V2.csv`
2. `data/output/CandidatePairs_ProductNameVerification_V2.csv`
3. `data/output/CandidatePairs_CategoryVerification_V2.csv`
4. `data/output/CandidatePairs_ColorVerification_V2.csv`
5. `data/output/CandidatePairs_SizeVerification_V2.csv`
6. `data/output/CandidatePairs_MaterialVerification_V2.csv`

Then run:

```powershell
python apply_decision_rules_v2.py
```

This creates `data/output/CandidatePairs_RuleBasedDecisions_V2.csv`.

## Validation safeguards

Each stage checks required columns, 185 expected candidate rows, nonblank CandidatePairID values, and uniqueness of CandidatePairID before writing its output. A failed stage stops the runner. The existing original CSV files are not changed.

## Important interpretation

`UNKNOWN` means the current deterministic verifier cannot establish equality or a confirmed difference. It is not equivalent to `MISMATCH`. Product-name differences remain `UNKNOWN` unless normalization proves equivalence; this package does not guess that different names mean different models. Color and numeric size comparisons can return `MISMATCH` only under the explicit checks implemented in the verifier.

The `MATCH` rule requires all five identity attributes to be confirmed as `EXACT_MATCH` or `NORMALIZED_MATCH`. A confirmed mismatch in any one of those five produces `NO_MATCH`. If there is no confirmed mismatch but at least one required attribute is `UNKNOWN`, the result is `REVIEW`. Material is reported separately as supporting evidence.

The fixed expected row count is currently 185, matching this assignment's candidate batch. If the candidate batch size changes, update `EXPECTED_CANDIDATE_COUNT` in the six verification scripts and `apply_decision_rules_v2.py` before running.
