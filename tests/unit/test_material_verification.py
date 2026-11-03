import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.matching.attribute_verification import (
    NormalizeMaterial,
    VerifyMaterial
)
from ai_matching.config.attribute_rules import (
    EXACT_MATCH,
    NORMALIZED_MATCH,
    UNKNOWN
)


def test_material_normalization():
    assert NormalizeMaterial("Cotton") == "cotton"
    assert NormalizeMaterial("COTTON") == "cotton"
    assert NormalizeMaterial("Cotton/Polyester") == "cotton polyester"
    assert NormalizeMaterial("Polyester-Cotton") == "cotton polyester"
    assert NormalizeMaterial("Mesh/Leather") == "leather mesh"
    assert NormalizeMaterial("Leather, Mesh") == "leather mesh"
    assert NormalizeMaterial("100% Cotton") == "100 cotton"
    assert NormalizeMaterial("Genuine Leather") == "genuine leather"
    assert NormalizeMaterial(None) is None


def test_material_verification():
    # Original exact match
    assert VerifyMaterial("Cotton", "Cotton") == EXACT_MATCH

    # Different separators and ordering
    assert VerifyMaterial(
        "Cotton/Polyester",
        "Polyester-Cotton"
    ) == NORMALIZED_MATCH

    assert VerifyMaterial(
        "Mesh/Leather",
        "Leather, Mesh"
    ) == NORMALIZED_MATCH

    # Composition percentage must be preserved
    assert VerifyMaterial(
        "100% Cotton",
        "Cotton"
    ) == UNKNOWN

    # Different material descriptors
    assert VerifyMaterial(
        "Genuine Leather",
        "Leather"
    ) == UNKNOWN

    assert VerifyMaterial(
        "Genuine Leather",
        "Synthetic Leather"
    ) == UNKNOWN

    # Different materials
    assert VerifyMaterial(
        "Polyester",
        "Nylon"
    ) == UNKNOWN

    # Missing material
    assert VerifyMaterial(None, "Cotton") == UNKNOWN

    # Empty material
    assert VerifyMaterial("", "Cotton") == UNKNOWN


if __name__ == "__main__":
    test_material_normalization()
    test_material_verification()
    print("All material verification tests passed.")
