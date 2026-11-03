"""
Unit test for attribute rules and outcomes configuration.
"""
import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.config.attribute_rules import (
    ATTRIBUTE_RULES,
    VERIFICATION_OUTCOMES,
    NON_IDENTITY_ATTRIBUTES
)


def test_attribute_rules():
    ExpectedAttributes = [
        "Brand",
        "ProductName",
        "Category",
        "Color",
        "Size",
        "Material",
        "Description",
        "Price",
        "Stock"
    ]

    assert list(ATTRIBUTE_RULES.keys()) == ExpectedAttributes

    for AttributeName, Rules in ATTRIBUTE_RULES.items():
        assert "SourceColumns" in Rules
        assert "ComparisonType" in Rules
        assert "IdentityAttribute" in Rules or AttributeName == "Stock"

    assert len(VERIFICATION_OUTCOMES) == 5

    assert NON_IDENTITY_ATTRIBUTES == [
        "Description",
        "Price",
        "Stock"
    ]


if __name__ == "__main__":
    test_attribute_rules()
    print("Attribute verification configuration validated.")
    print(f"Total Attributes: {len(ATTRIBUTE_RULES)}")
    print(f"Verification Outcomes: {len(VERIFICATION_OUTCOMES)}")
