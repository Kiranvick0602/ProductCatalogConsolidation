# ProductCatalogConsolidation – Enterprise Product Matching & Catalog Consolidation

## 1. Executive Summary

`ProductCatalogConsolidation` is a production-grade Python data and AI engineering framework designed to reconcile, match, and consolidate disparate e-commerce product catalogs from **StyleHaus** and **UrbanThread**.

The pipeline combines deterministic attribute verification, high-dimensional vector embeddings (`nomic-embed-text-v1.5`), and conservative local LLM validation (`phi-3-mini-4k-instruct` via LM Studio) to produce a unified Gold Product Catalog ready for Microsoft Fabric Lakehouse ingestion.

---

## 2. Architecture & Pipeline Workflow

```
                                  +-----------------------+
                                  |   CandidatePairs.csv  |
                                  |      (185 pairs)      |
                                  +-----------+-----------+
                                              |
                   +--------------------------+--------------------------+
                   |                                                     |
                   v                                                     v
      [Feature & Embedding Pipeline]                            [Deterministic Verifiers]
  scripts/embeddings/build_canonical_product_text.py      ai_matching/matching/attribute_verification.py
                   |                                      ai_matching/matching/product_model_verification.py (V4.3.1)
                   v                                      ai_matching/matching/color_verification.py (V3.1)
  CandidatePairs_CanonicalText.csv                                       |
                   |                                                     v
                   v                                    Phase 5.5 Cumulative Attribute Pipeline
  ai_matching/embeddings/generate_product_embeddings.py           (Brand, Name, Cat, Color, Size, Mat)
                   |                                                     |
                   v                                                     v
  ProductEmbeddings.jsonl (768-dim vectors)             CandidatePairs_ColorVerification_V3_1.csv
                   |                                                     |
                   v                                                     |
  scripts/matching/calculate_candidate_similarity.py                     |
                   |                                                     |
                   +--------------------------+--------------------------+
                                              |
                                              v
                              +-------------------------------+
                              |    Phase 5.6 Decision Engine  |
                              |   (scripts/matching/run_final |
                              |    _matching_decisions.py)    |
                              +---------------+---------------+
                                              |
                     +------------------------+------------------------+
                     |                        |                        |
                     v                        v                        v
             +---------------+        +---------------+        +---------------+
             |   NO_MATCH    |        |     REVIEW    |        |     MATCH     |
             |  (155 pairs)  |        |   (8 pairs)   |        |  (22 pairs)   |
             +---------------+        +-------+-------+        +---------------+
                                              |
                                              v
                              +-------------------------------+
                              |   Phase 5.7 Phi-3 Validation  |
                              |   (scripts/llm/validate_      |
                              |    review_pairs_phi3.py)      |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |     Phase 5.8 Adjudication    |
                              |  (scripts/matching/finalize_  |
                              |   phase5_8_decisions.py)      |
                              |  Phi3DecisionAccepted = False |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |   Phase 5.9 OneLake Export    |
                              |   (scripts/export/write_      |
                              |    phase5_9_to_onelake.py)    |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |    Phase 5.10 Fabric Delta    |
                              |       Lakehouse Tables        |
                              +-------------------------------+
```

---

## 3. Finalized Business Logic

The deterministic decision logic strictly adheres to approved requirements:
1. **Product Model Verification (V4.3.1):**
   - Brand-aware token stripping, shoe/waist size removal, and substantive model number comparison.
   - Enforces approved specific rulings: Converse Chuck Taylor vs. Run Star (`DIFFERENT_MODEL`), Air Jordan 1 High OG vs. Bred (`UNKNOWN`), and Barbour Bedale vs. Ashby (`DIFFERENT_MODEL`).
2. **Color Verification (V3.1):**
   - Brand prefix stripping (e.g. `TNF Black` $\rightarrow$ `black`), alias canonicalization (`core black`, `optical white`, `varsity red`), and multi-color set equality.
   - Partial composite overlap returns `MISMATCH` (e.g., `White/Black` vs `Black/Red`).
3. **Size Verification:**
   - Standardizes apparel sizes (`xs`–`xxxl`), formats system prefixes (`US`, `UK`, `EU`), and treats bare numeric footwear sizes as equivalent to US-prefixed sizes.
   - For `SAME_MODEL` rows with `UNKNOWN` where both explicit raw labels exist and differ (e.g., M vs L), resolves to `MISMATCH`.
4. **Final Matching Decision Rule:**
   - Confirmed mismatch in brand, model, color, or size $\rightarrow$ **`NO_MATCH`**.
   - Any unresolved critical attribute $\rightarrow$ **`REVIEW`**.
   - All critical attributes verified $\rightarrow$ **`MATCH`**.
   - Non-critical attributes (category, material, price, similarity) do not override critical conflicts.
5. **Final Decision Baseline Counts:**
   - **`MATCH`:** 22
   - **`NO_MATCH`:** 155
   - **`REVIEW`:** 8
   - **Total Candidates:** 185

---

## 4. Directory Structure

```text
ProductCatalogConsolidation/
│
├── ai_matching/                         # Reusable core library packages
│   ├── config/
│   │   ├── attribute_rules.py           # Attribute verification rules & outcomes
│   │   └── settings.py                  # Environment-aware settings & paths
│   ├── embeddings/
│   │   ├── extract_unique_products.py   # Extract unique products from candidates
│   │   ├── generate_product_embeddings.py # LM Studio Nomic embed client with checkpointing
│   │   └── validate_product_embeddings.py # Vector validation & text hash integrity
│   ├── llm/
│   │   └── phi3_client.py               # LM Studio Phi-3 client, prompts & schema validation
│   ├── matching/
│   │   ├── attribute_verification.py    # V2 verification (Brand, Category, Size, Material)
│   │   ├── color_verification.py        # Approved V3.1 Color Verification
│   │   ├── product_model_verification.py # Approved V4.3.1 Product Model Verification
│   │   ├── cosine_similarity.py         # Vector similarity calculation
│   │   └── final_decision.py            # Final Deterministic Decision Engine
│   └── utils/
│       └── canonical_text.py            # Canonical product text generation
│
├── scripts/                             # Executable command-line pipeline stages
│   ├── embeddings/
│   │   └── build_canonical_product_text.py # Generates canonical text CSV for embeddings
│   ├── matching/
│   │   ├── calculate_candidate_similarity.py # Computes embedding cosine similarity
│   │   ├── run_attribute_verification_v2.py  # Orchestrates 6 attribute verifications
│   │   ├── verify_candidate_brands.py
│   │   ├── verify_candidate_product_names.py
│   │   ├── verify_candidate_categories.py
│   │   ├── verify_candidate_colors_v3_1.py   # Approved V3.1 color runner
│   │   ├── verify_candidate_sizes.py
│   │   ├── verify_candidate_materials.py
│   │   ├── verify_candidate_product_models_v4_3_1.py # Approved V4.3.1 model runner
│   │   ├── run_final_matching_decisions.py   # Phase 5.6 deterministic engine runner
│   │   └── finalize_phase5_8_decisions.py    # Phase 5.8 final adjudication runner
│   ├── llm/
│   │   └── validate_review_pairs_phi3.py     # Phase 5.7 Phi-3 review validation runner
│   ├── export/
│   │   └── write_phase5_9_to_onelake.py      # Phase 5.9 OneLake Parquet exporter
│   └── diagnostics/                          # Diagnostic, inspection & audit utilities
│       ├── analyze_unknown_source_values.py
│       ├── analyze_verification_distribution.py
│       ├── audit_color_size_mismatches.py
│       ├── audit_color_v3_vs_v3_1.py
│       ├── audit_v4_2_vs_v4_3_1_product_models.py
│       ├── compare_verification_v1_v2.py
│       ├── inspect_unknown_match_attributes.py
│       ├── inspect_verification_columns.py
│       ├── validate_candidate_input.py
│       ├── test_lm_studio_connection.py
│       ├── analyze_llm_candidates.py
│       ├── analyze_llm_decision_quality.py
│       ├── clean_phi3_checkpoint.py
│       └── prepare_match_calibration.py
│
├── tests/                               # Automated test suites (Pytest compatible)
│   ├── conftest.py                      # Global test fixtures and sys.path configuration
│   ├── unit/
│   │   ├── test_attribute_rules.py
│   │   ├── test_brand_verification.py
│   │   ├── test_category_verification.py
│   │   ├── test_material_verification.py
│   │   ├── test_product_name_verification.py
│   │   ├── test_size_verification.py
│   │   └── test_attribute_verification.py
│   ├── regression/
│   │   ├── test_product_model_v4_3_1.py      # Approved V4.3.1 regression suite (15 cases)
│   │   ├── test_color_verification_v3_1.py   # Approved V3.1 regression suite (22 cases)
│   │   └── test_final_matching_decision.py   # Deterministic decision regression suite (9 cases)
│   └── integration/                          # LM Studio dependent tests
│       ├── test_nomic_embedding.py
│       └── test_phi3_client.py
│
├── data/                                # Protected datasets and evaluation outputs
│   ├── input/                           # CandidatePairs.csv
│   ├── embeddings/                      # ProductEmbeddings.jsonl, UniqueProducts.csv
│   └── output/                          # CandidatePairs_*.csv and quality audits
│
├── archive/                             # Preserved historical code and superseded versions
│   ├── legacy_matching/                 # V1 verifiers and older decision runners
│   ├── product_model_audit/             # V3 - V4.3 model scripts and audits
│   ├── color_verification/              # V3 color verification runner
│   ├── legacy_llm/                      # Full batch candidate runner
│   └── legacy_tests/                    # Superseded V1/V3 tests
│
├── api/                                 # Empty scaffold for future FastAPI development
├── notebooks/                           # Empty scaffold for future Lakehouse notebooks
├── requirements.txt                     # Pinned and validated dependencies
├── .env.example                         # Template for local environment configuration
├── .gitignore                           # Standard gitignore
└── README.md                            # Comprehensive project documentation
```

---

## 5. Environment Setup Instructions

### 5.1 Fresh Virtual Environment Setup
```powershell
# 1. Create a virtual environment with Python 3.12 or 3.15
python -m venv .venv

# 2. Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment variables
Copy-Item .env.example .env
```

---

## 6. Pipeline Execution Instructions

Run all pipeline commands from the `ProductCatalogConsolidation` project root:

### Stage 1: Embedding Preparation & Similarity
```powershell
# Generate canonical product text
python scripts/embeddings/build_canonical_product_text.py

# Compute embedding cosine similarity
python scripts/matching/calculate_candidate_similarity.py
```

### Stage 2: Attribute Verification Pipeline
```powershell
# Run the 6 core attribute verifications
python scripts/matching/run_attribute_verification_v2.py

# Run approved V4.3.1 Product Model Verification
python scripts/matching/verify_candidate_product_models_v4_3_1.py

# Run approved V3.1 Color Verification
python scripts/matching/verify_candidate_colors_v3_1.py
```

### Stage 3: Phase 5.6 Final Deterministic Decisions
```powershell
python scripts/matching/run_final_matching_decisions.py
```
*Expected Output:*
- Total records: 185
- **`NO_MATCH`:** 155
- **`MATCH`:** 22
- **`REVIEW`:** 8

### Stage 4: Phase 5.7 Phi-3 Validation (Requires LM Studio)
*Prerequisite:* Ensure LM Studio is running locally on port 1234 with model `phi-3-mini-4k-instruct` loaded.
```powershell
python scripts/llm/validate_review_pairs_phi3.py
```
*Note:* Only the 8 `REVIEW` records are evaluated.

### Stage 5: Phase 5.8 Final Decision Consolidation
```powershell
python scripts/matching/finalize_phase5_8_decisions.py
```
*Preserves 22 MATCH, 155 NO_MATCH, 8 REVIEW. Explicitly documents `Phi3DecisionAccepted = False`.*

### Stage 6: Phase 5.9 OneLake Export
```powershell
python scripts/export/write_phase5_9_to_onelake.py --onelake-files-path "C:\path\to\ProductCatalogLakehouse.Lakehouse\Files"
```
*Exports `FinalMatchingDecisions.parquet`, `Phi3ValidationResults.parquet`, `FinalMatchingSummary.parquet`, and `manifest.json`.*

---

## 7. Automated Testing Instructions

Run test discovery across all unit, regression, and integration suites:
```powershell
# Run entire automated test suite
pytest tests -v

# Run only regression suites (V4.3.1 product model, V3.1 color, final decisions)
pytest tests/regression -v

# Run unit tests
pytest tests/unit -v

# Run LM Studio integration tests (requires LM Studio running)
pytest tests/integration -v -m lm_studio
```

*Current Suite Baseline:*
- **71 Total Tests:** 69 Passed, 2 Skipped (LM Studio offline), 0 Failed.
