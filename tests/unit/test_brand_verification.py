import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.attribute_verification import (
    NormalizeBrand,
    VerifyBrand
)
from ai_matching.config.attribute_rules import (
    EXACT_MATCH,
    NORMALIZED_MATCH,
    MISMATCH,
    UNKNOWN
)


def test_brand_normalization():
    assert NormalizeBrand("Nike") == "nike"
    assert NormalizeBrand("Ray-Ban") == "ray ban"
    assert NormalizeBrand("Ray Ban") == "ray ban"
    assert NormalizeBrand("  ADIDAS  ") == "adidas"
    assert NormalizeBrand(None) is None


def test_brand_verification():
    TestCases = [
        ("Nike", "Nike", EXACT_MATCH),
        ("Nike", "NIKE", NORMALIZED_MATCH),
        ("Ray-Ban", "Ray Ban", NORMALIZED_MATCH),
        ("Adidas", "ADIDAS", NORMALIZED_MATCH),
        ("Nike", "Adidas", MISMATCH),
        (None, "Nike", UNKNOWN),
        ("", "Nike", UNKNOWN),
        ("Nike", "", UNKNOWN)
    ]

    for StyleHausBrand, UrbanThreadBrand, ExpectedResult in TestCases:
        ActualResult = VerifyBrand(StyleHausBrand, UrbanThreadBrand)
        assert ActualResult == ExpectedResult, (
            f"Failed: {StyleHausBrand} vs {UrbanThreadBrand}. "
            f"Expected {ExpectedResult}, got {ActualResult}"
        )


if __name__ == "__main__":
    test_brand_normalization()
    test_brand_verification()
    print("All brand verification tests passed.")
