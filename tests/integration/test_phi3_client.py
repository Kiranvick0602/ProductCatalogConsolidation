"""
Integration test for Phi-3 Mini Instruct LLM validation via LM Studio.
Requires LM Studio running locally at http://localhost:1234 with phi-3-mini-4k-instruct.
"""
import sys
from pathlib import Path
import pytest
import requests
import pandas as pd

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.config.settings import LM_STUDIO_MODELS_ENDPOINT
from ai_matching.llm.phi3_client import CallPhi3


def is_lm_studio_available():
    try:
        res = requests.get(LM_STUDIO_MODELS_ENDPOINT, timeout=3)
        return res.status_code == 200
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.lm_studio
def test_phi3_client_inference():
    if not is_lm_studio_available():
        pytest.skip("LM Studio is not running or unreachable at " + LM_STUDIO_MODELS_ENDPOINT)

    input_file = ProjectRoot / "data" / "output" / "CandidatePairs_MaterialVerification.csv"
    if not input_file.exists():
        pytest.skip(f"Input file not found: {input_file}")

    pair_id = "84966b11c34a171815af170136a83719a1e9833adbfd9c205724c82e34543501"
    candidate_df = pd.read_csv(input_file, dtype=str, keep_default_na=False)
    candidate = candidate_df.loc[candidate_df["CandidatePairID"] == pair_id]
    if candidate.empty:
        pytest.skip(f"Candidate pair not found: {pair_id}")

    candidate_record = candidate.iloc[0].to_dict()
    result = CallPhi3(candidate_record)

    assert result is not None
    assert "Phi3ValidationDecision" in result
    assert result["Phi3ValidationDecision"] in {"MATCH", "NO_MATCH", "REVIEW"}
    assert "Phi3Confidence" in result


if __name__ == "__main__":
    if not is_lm_studio_available():
        print("ERROR: LM Studio is not reachable at http://localhost:1234.")
        print("Start LM Studio and load 'phi-3-mini-4k-instruct' to run this test.")
        sys.exit(1)
    test_phi3_client_inference()
    print("Phi-3 client integration test passed.")
