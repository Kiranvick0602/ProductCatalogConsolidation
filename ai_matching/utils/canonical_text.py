import pandas as pd


# ============================================================
# HELPER FUNCTION: GET CLEAN ATTRIBUTE VALUE
# ============================================================

def GetAttributeValue(
    Record,
    NormalizedColumn,
    OriginalColumn=None
):

    """
    Retrieves a normalized attribute value.

    If the normalized value is missing or empty,
    falls back to the original attribute value.
    """

    Value = Record.get(NormalizedColumn)

    if pd.isna(Value) or str(Value).strip() == "":

        if OriginalColumn:

            Value = Record.get(OriginalColumn)

    if pd.isna(Value) or Value is None:

        return ""

    return " ".join(str(Value).strip().split())


# ============================================================
# BUILD CANONICAL PRODUCT TEXT
# ============================================================

def BuildCanonicalProductText(
    Record,
    Source
):

    """
    Builds canonical product text for either
    StyleHaus or UrbanThread.
    """

    if Source not in ["StyleHaus", "UrbanThread"]:

        raise ValueError(
            f"Unsupported product source: {Source}"
        )

    # --------------------------------------------------------
    # Determine source-specific column names
    # --------------------------------------------------------

    ProductName = GetAttributeValue(
        Record,
        f"{Source}_NormalizedProductName",
        f"{Source}_ProductName"
    )

    Category = GetAttributeValue(
        Record,
        f"{Source}_NormalizedCategory",
        f"{Source}_Category"
    )

    Description = GetAttributeValue(
        Record,
        f"{Source}_NormalizedDescription",
        f"{Source}_Description"
    )

    Color = GetAttributeValue(
        Record,
        f"{Source}_NormalizedColor",
        f"{Source}_Color"
    )

    Size = GetAttributeValue(
        Record,
        f"{Source}_NormalizedSize",
        f"{Source}_Size"
    )

    Material = GetAttributeValue(
        Record,
        f"{Source}_NormalizedMaterial",
        f"{Source}_Material"
    )

    Brand = GetAttributeValue(
        Record,
        "CanonicalBrand"
    )

    # --------------------------------------------------------
    # Construct canonical text
    # --------------------------------------------------------

    Attributes = [
        ("Brand", Brand),
        ("Product Name", ProductName),
        ("Category", Category),
        ("Description", Description),
        ("Color", Color),
        ("Size", Size),
        ("Material", Material)
    ]

    CanonicalText = "\n".join(
        f"{Attribute}: {Value}"
        for Attribute, Value in Attributes
        if Value
    )

    return CanonicalText