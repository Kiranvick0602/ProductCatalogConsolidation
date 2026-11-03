import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.attribute_verification import (
    NormalizeCategory,
    VerifyCategory
)
from ai_matching.config.attribute_rules import (
    EXACT_MATCH,
    NORMALIZED_MATCH,
    UNKNOWN
)


def test_category_normalization():
    assert NormalizeCategory("Men's Lifestyle Shoes") == "lifestyle men shoes"
    assert NormalizeCategory("LIFESTYLE SHOES - MEN") == "lifestyle men shoes"
    assert NormalizeCategory("Men's Running Shoes") == "men running shoes"
    assert NormalizeCategory("RUNNING SHOES - MEN") == "men running shoes"
    assert NormalizeCategory(None) is None


def test_category_verification():
    # Original exact match
    assert VerifyCategory("Men's Shoes", "Men's Shoes") == EXACT_MATCH

    # Normalized match
    assert VerifyCategory(
        "Men's Lifestyle Shoes",
        "LIFESTYLE SHOES - MEN"
    ) == NORMALIZED_MATCH

    # Different categories
    assert VerifyCategory(
        "Men's Running Shoes",
        "Men's Outerwear"
    ) == UNKNOWN

    # Missing category
    assert VerifyCategory(None, "Men's Shoes") == UNKNOWN

    # Empty category
    assert VerifyCategory("", "Men's Shoes") == UNKNOWN


if __name__ == "__main__":
    test_category_normalization()
    test_category_verification()
    print("All category verification tests passed.")
