import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.attribute_verification import (
    NormalizeSize,
    VerifySize
)
from ai_matching.config.attribute_rules import (
    EXACT_MATCH,
    NORMALIZED_MATCH,
    UNKNOWN
)


def test_size_normalization():
    assert NormalizeSize("M") == "m"
    assert NormalizeSize("Medium") == "m"
    assert NormalizeSize("XL") == "xl"
    assert NormalizeSize("Extra Large") == "xl"

    # In V2 normalization, bare numeric size and US-prefixed numeric size normalize to bare number
    assert NormalizeSize("US10") == "10"
    assert NormalizeSize("US 10") == "10"

    assert NormalizeSize("EU42") == "eu 42"
    assert NormalizeSize("EU 42") == "eu 42"
    assert NormalizeSize("10") == "10"
    assert NormalizeSize(None) is None


def test_size_verification():
    # Original exact match
    assert VerifySize("M", "M") == EXACT_MATCH

    # Apparel-size normalization
    assert VerifySize("M", "Medium") == NORMALIZED_MATCH
    assert VerifySize("XL", "Extra Large") == NORMALIZED_MATCH

    # Sizing-system formatting
    assert VerifySize("US10", "US 10") == NORMALIZED_MATCH
    assert VerifySize("10", "US 10") == NORMALIZED_MATCH
    assert VerifySize("EU42", "EU 42") == NORMALIZED_MATCH

    # Different sizing systems
    assert VerifySize("US 10", "UK 10") == UNKNOWN

    # Different apparel sizes without model context
    assert VerifySize("M", "L") == UNKNOWN

    # Missing size
    assert VerifySize(None, "M") == UNKNOWN
    assert VerifySize("", "M") == UNKNOWN


if __name__ == "__main__":
    test_size_normalization()
    test_size_verification()
    print("All size verification tests passed.")
