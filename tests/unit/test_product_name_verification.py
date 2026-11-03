import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.attribute_verification import (
    NormalizeProductName,
    VerifyProductName
)
from ai_matching.config.attribute_rules import (
    EXACT_MATCH,
    NORMALIZED_MATCH,
    UNKNOWN
)


def test_product_name_normalization():
    assert (
        NormalizeProductName("Nike Air Max 90 - White/Black")
        == "nike air max 90 white black"
    )

    # In V2 normalization, 'airmax' token is canonicalized to 'air max'
    assert (
        NormalizeProductName("NIKE AIRMAX 90 WHITE BLACK")
        == "nike air max 90 white black"
    )

    assert (
        NormalizeProductName("  Adidas Gazelle  ")
        == "adidas gazelle"
    )

    assert NormalizeProductName(None) is None


def test_product_name_verification():
    # In V2, product-name differences remain UNKNOWN unless normalization proves equivalence
    TestCases = [
        ("Nike Air Max 90", "Nike Air Max 90", 1.0, EXACT_MATCH),
        ("Adidas Gazelle - Black/White", "ADIDAS GAZELLE BLACK WHITE", 1.0, NORMALIZED_MATCH),
        ("Nike Air Max 90", "Nike Air Max 97", 0.5, UNKNOWN),
        ("Nike Air Max 90", "Adidas Samba", 0.0, UNKNOWN),
        (None, "Nike Air Max 90", 0.8, UNKNOWN),
        ("Nike Air Max 90", "Nike Air Max 90", None, EXACT_MATCH),
        ("Nike Air Max 90", "Nike Air Max 97", None, UNKNOWN)
    ]

    for (
        StyleHausName,
        UrbanThreadName,
        Similarity,
        ExpectedResult
    ) in TestCases:
        ActualResult = VerifyProductName(
            StyleHausName,
            UrbanThreadName,
            Similarity
        )
        assert ActualResult == ExpectedResult, (
            f"Failed: {StyleHausName} vs {UrbanThreadName}. "
            f"Expected {ExpectedResult}, got {ActualResult}"
        )


if __name__ == "__main__":
    test_product_name_normalization()
    test_product_name_verification()
    print("\nAll product name verification tests passed.")
