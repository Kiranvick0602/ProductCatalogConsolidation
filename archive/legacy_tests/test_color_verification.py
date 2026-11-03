from ai_matching.matching.attribute_verification import (
    NormalizeColor,
    VerifyColor
)

from ai_matching.config.attribute_rules import (
    EXACT_MATCH,
    NORMALIZED_MATCH,
    UNKNOWN
)


def TestColorNormalization():

    assert NormalizeColor("Black") == "black"

    assert NormalizeColor("BLACK") == "black"

    assert NormalizeColor("Grey") == "gray"

    assert NormalizeColor("Gray") == "gray"

    assert NormalizeColor("Black/White") == "black white"

    assert NormalizeColor("White-Black") == "black white"

    assert NormalizeColor("Navy Blue") == "blue navy"

    assert NormalizeColor(None) is None

    print("Color normalization tests passed.")


def TestColorVerification():

    # Original exact match
    assert VerifyColor(
        "Black",
        "Black"
    ) == EXACT_MATCH

    # Normalized spelling match
    assert VerifyColor(
        "Grey",
        "Gray"
    ) == NORMALIZED_MATCH

    # Different separators and word order
    assert VerifyColor(
        "Black/White",
        "White-Black"
    ) == NORMALIZED_MATCH

    # Different color descriptions
    assert VerifyColor(
        "Navy Blue",
        "Navy"
    ) == UNKNOWN

    # Different colors
    assert VerifyColor(
        "Black",
        "Red"
    ) == UNKNOWN

    # Missing color
    assert VerifyColor(
        None,
        "Black"
    ) == UNKNOWN

    # Empty color
    assert VerifyColor(
        "",
        "Black"
    ) == UNKNOWN

    print("Color verification tests passed.")


if __name__ == "__main__":

    TestColorNormalization()

    TestColorVerification()

    print("All color verification tests passed.")