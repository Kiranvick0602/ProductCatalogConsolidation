"""
Integration test for Nomic Embedding API via LM Studio.
Requires LM Studio running locally at http://localhost:1234 with text-embedding-nomic-embed-text-v1.5.
"""
import sys
from pathlib import Path
import pytest
import requests
import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.config.settings import (
    LM_STUDIO_EMBEDDINGS_ENDPOINT,
    LM_STUDIO_MODELS_ENDPOINT,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_TASK_PREFIX,
    EMBEDDING_TIMEOUT
)


def is_lm_studio_available():
    try:
        res = requests.get(LM_STUDIO_MODELS_ENDPOINT, timeout=3)
        return res.status_code == 200
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.lm_studio
def test_nomic_embedding_generation():
    if not is_lm_studio_available():
        pytest.skip("LM Studio is not running or unreachable at " + LM_STUDIO_MODELS_ENDPOINT)

    candidate_file = ProjectRoot / "data" / "output" / "CandidatePairs_CanonicalText.csv"
    if not candidate_file.exists():
        pytest.skip(f"Input file not found: {candidate_file}")

    df = pd.read_csv(candidate_file, encoding="utf-8")
    product_text = df.loc[0, "StyleHaus_CanonicalText"]
    formatted_input = f"{EMBEDDING_TASK_PREFIX}{product_text}"

    payload = {
        "model": EMBEDDING_MODEL_NAME,
        "input": formatted_input
    }

    response = requests.post(
        LM_STUDIO_EMBEDDINGS_ENDPOINT,
        json=payload,
        timeout=EMBEDDING_TIMEOUT
    )
    assert response.status_code == 200, f"HTTP Error {response.status_code}: {response.text}"
    result = response.json()
    assert "data" in result
    assert len(result["data"]) > 0
    vector = result["data"][0]["embedding"]
    assert len(vector) == 768, f"Expected 768-dim vector, got {len(vector)}"


if __name__ == "__main__":
    if not is_lm_studio_available():
        print("ERROR: LM Studio is not reachable at http://localhost:1234.")
        print("Start LM Studio and load 'text-embedding-nomic-embed-text-v1.5' to run this test.")
        sys.exit(1)
    test_nomic_embedding_generation()
    print("Nomic embedding integration test passed.")
