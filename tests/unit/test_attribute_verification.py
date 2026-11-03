"""
Unit tests for V2 Attribute Verification rules (Product Name, Color, Size, Material).
Consolidates test cases from test_attribute_verification_updates.py into standard pytest test functions.
"""
import sys
from pathlib import Path
import pytest

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.attribute_verification import (
    VerifyProductName,
    VerifyColor,
    VerifySize,
    VerifyMaterial,
    NormalizeProductName,
    NormalizeSize,
    NormalizeColor,
    NormalizeMaterial
)

UPDATE_TEST_CASES = [
    ("Product Name - Joined Token Match", VerifyProductName, "Nike Air Max 90 - White/Black", "NIKE AIRMAX 90 WHT BLK", "NORMALIZED_MATCH"),
    ("Product Name - Different Model Match", VerifyProductName, "Adidas Ultraboost 22", "Adidas NMD R1", "UNKNOWN"),
    ("Color - Normalized Navy Match", VerifyColor, "Navy", "Navy Blue", "NORMALIZED_MATCH"),
    ("Color - Clear Mismatch", VerifyColor, "White", "Navy Blue", "MISMATCH"),
    ("Color - Brand Prefix Alias Match", VerifyColor, "TNF Black", "Black", "NORMALIZED_MATCH"),
    ("Color - Wash Synonym Unresolved", VerifyColor, "Medium Stonewash", "Medium Wash", "UNKNOWN"),
    ("Size - US Footwear Prefix Match", VerifySize, "10", "US 10", "NORMALIZED_MATCH"),
    ("Size - Footwear Size Mismatch", VerifySize, "10", "US 11", "MISMATCH"),
    ("Material - Multi-component Subset Match", VerifyMaterial, "Mesh/Leather", "Mesh, Leather upper", "NORMALIZED_MATCH"),
    ("Material - Partial Material Composite", VerifyMaterial, "Leather/Suede", "Leather", "UNKNOWN"),
]


@pytest.mark.parametrize("name,func,val1,val2,expected", UPDATE_TEST_CASES)
def test_attribute_verification_case(name, func, val1, val2, expected):
    result = func(val1, val2)
    assert result == expected, f"Failed {name}: expected {expected}, got {result}"


def test_normalize_product_name_joined_tokens():
    assert NormalizeProductName("NIKE AIRMAX 90 WHT BLK") == "nike air max 90 white black"
    assert NormalizeProductName("Airforce 1 07") == "air force 1 07"


def test_normalize_size_footwear():
    assert NormalizeSize("US 10") == "10"
    assert NormalizeSize("US10") == "10"
    assert NormalizeSize("Medium") == "m"
    assert NormalizeSize("Large") == "l"


if __name__ == "__main__":
    for name, func, val1, val2, expected in UPDATE_TEST_CASES:
        res = func(val1, val2)
        status = "PASS" if res == expected else "FAIL"
        print(f"{status}: {name} => {res} (expected {expected})")
