import re

from ai_matching.config.attribute_rules import (
    EXACT_MATCH,
    NORMALIZED_MATCH,
    PARTIAL_MATCH,
    MISMATCH,
    UNKNOWN
)

# ============================================================
# PRODUCT NAME NORMALIZATION
# ============================================================

def NormalizeProductName(ProductName):

    if ProductName is None:
        return None

    ProductName = str(ProductName).strip().lower()

    if not ProductName:
        return None

    # Replace punctuation with spaces
    ProductName = re.sub(
        r"[^a-z0-9\s]",
        " ",
        ProductName
    )

    # Normalize multiple spaces
    ProductName = re.sub(
        r"\s+",
        " ",
        ProductName
    ).strip()

    return ProductName


# ============================================================
# PRODUCT NAME VERIFICATION
# ============================================================

def VerifyProductName(
    StyleHausProductName,
    UrbanThreadProductName,
    ProductNameSimilarity=None
):

    # Handle missing values
    if (
        StyleHausProductName is None
        or UrbanThreadProductName is None
    ):
        return UNKNOWN

    if (
        str(StyleHausProductName).strip() == ""
        or str(UrbanThreadProductName).strip() == ""
    ):
        return UNKNOWN

    # Check original exact equality
    if (
        str(StyleHausProductName).strip()
        == str(UrbanThreadProductName).strip()
    ):
        return EXACT_MATCH

    # Normalize product names
    StyleHausNormalizedName = NormalizeProductName(
        StyleHausProductName
    )

    UrbanThreadNormalizedName = NormalizeProductName(
        UrbanThreadProductName
    )

    # Check normalized equality
    if StyleHausNormalizedName == UrbanThreadNormalizedName:
        return NORMALIZED_MATCH

    # Different names require further verification
    return UNKNOWN

# ============================================================
# BRAND NORMALIZATION
# ============================================================

def NormalizeBrand(Brand):

    if Brand is None:
        return None

    Brand = str(Brand).strip()

    if not Brand:
        return None

    # Convert to lowercase
    Brand = Brand.lower()

    # Replace punctuation and special characters with spaces
    Brand = re.sub(r"[^a-z0-9\s]", " ", Brand)

    # Normalize multiple spaces
    Brand = re.sub(r"\s+", " ", Brand).strip()

    return Brand

def NormalizeCategory(Category):

    if Category is None:
        return None

    Category = str(Category).strip().lower()

    if not Category:
        return None

    # Normalize possessive gender terms before removing punctuation
    Category = re.sub(r"\bmen's\b", "men", Category)
    Category = re.sub(r"\bwomen's\b", "women", Category)

    # Replace punctuation and separators with spaces
    Category = re.sub(r"[^a-z0-9\s]", " ", Category)

    # Normalize whitespace
    Category = re.sub(r"\s+", " ", Category).strip()

    # Standardize gender terms
    Category = re.sub(r"\bmens\b", "men", Category)
    Category = re.sub(r"\bwomens\b", "women", Category)

    # Sort tokens to handle different word orders
    CategoryTokens = sorted(Category.split())

    return " ".join(CategoryTokens)

def VerifyCategory(
    StyleHausCategory,
    UrbanThreadCategory
):

    # Handle missing values
    if (
        StyleHausCategory is None
        or UrbanThreadCategory is None
    ):
        return UNKNOWN

    StyleHausCategory = str(StyleHausCategory).strip()
    UrbanThreadCategory = str(UrbanThreadCategory).strip()

    if (
        not StyleHausCategory
        or not UrbanThreadCategory
    ):
        return UNKNOWN

    # Check original exact equality
    if StyleHausCategory == UrbanThreadCategory:
        return EXACT_MATCH

    # Normalize categories
    StyleHausNormalizedCategory = NormalizeCategory(
        StyleHausCategory
    )

    UrbanThreadNormalizedCategory = NormalizeCategory(
        UrbanThreadCategory
    )

    # Check normalized equality
    if StyleHausNormalizedCategory == UrbanThreadNormalizedCategory:
        return NORMALIZED_MATCH

    # Different categories require further verification
    return UNKNOWN

# ============================================================
# BRAND VERIFICATION
# ============================================================

def VerifyBrand(StyleHausBrand, UrbanThreadBrand):

    # Handle missing values
    if (
        StyleHausBrand is None
        or UrbanThreadBrand is None
    ):

        return UNKNOWN

    if (
        str(StyleHausBrand).strip() == ""
        or str(UrbanThreadBrand).strip() == ""
    ):

        return UNKNOWN

    # Check exact equality
    if str(StyleHausBrand).strip() == str(UrbanThreadBrand).strip():

        return EXACT_MATCH

    # Normalize both brands
    StyleHausNormalizedBrand = NormalizeBrand(
        StyleHausBrand
    )

    UrbanThreadNormalizedBrand = NormalizeBrand(
        UrbanThreadBrand
    )

    # Check normalized equality
    if StyleHausNormalizedBrand == UrbanThreadNormalizedBrand:

        return NORMALIZED_MATCH

    return MISMATCH

def NormalizeColor(Color):

    if Color is None:
        return None

    Color = str(Color).strip().lower()

    if not Color:
        return None

    # Standardize common spelling differences
    Color = re.sub(r"\bgrey\b", "gray", Color)

    # Replace separators and punctuation with spaces
    Color = re.sub(r"[^a-z0-9\s]", " ", Color)

    # Normalize whitespace
    Color = re.sub(r"\s+", " ", Color).strip()

    # Sort tokens because color order does not affect identity
    ColorTokens = sorted(Color.split())

    return " ".join(ColorTokens)

def VerifyColor(
    StyleHausColor,
    UrbanThreadColor
):

    # Handle missing values
    if (
        StyleHausColor is None
        or UrbanThreadColor is None
    ):
        return UNKNOWN

    StyleHausColor = str(StyleHausColor).strip()
    UrbanThreadColor = str(UrbanThreadColor).strip()

    if (
        not StyleHausColor
        or not UrbanThreadColor
    ):
        return UNKNOWN

    # Check original exact equality
    if StyleHausColor == UrbanThreadColor:
        return EXACT_MATCH

    # Normalize colors
    StyleHausNormalizedColor = NormalizeColor(
        StyleHausColor
    )

    UrbanThreadNormalizedColor = NormalizeColor(
        UrbanThreadColor
    )

    # Check normalized equality
    if StyleHausNormalizedColor == UrbanThreadNormalizedColor:
        return NORMALIZED_MATCH

    # Different color descriptions require further verification
    return UNKNOWN


def NormalizeSize(Size):

    if Size is None:
        return None

    Size = str(Size).strip().lower()

    if not Size:
        return None

    # Normalize whitespace
    Size = re.sub(r"\s+", " ", Size)

    # Standardize common apparel size descriptions
    SizeAliases = {
        "extra small": "xs",
        "x small": "xs",
        "small": "s",
        "medium": "m",
        "extra large": "xl",
        "x large": "xl",
        "extra extra large": "xxl",
        "2xl": "xxl",
        "3xl": "xxxl"
    }

    if Size in SizeAliases:
        return SizeAliases[Size]

    # Normalize recognized sizing-system formatting.
    # Examples: US10 -> us 10, EU42 -> eu 42
    Size = re.sub(
        r"\b(us|uk|eu)\s*(?=\d)",
        r"\1 ",
        Size
    )

    # Normalize whitespace again
    Size = re.sub(r"\s+", " ", Size).strip()

    return Size

def VerifySize(
    StyleHausSize,
    UrbanThreadSize
):

    # Handle missing values
    if (
        StyleHausSize is None
        or UrbanThreadSize is None
    ):
        return UNKNOWN

    StyleHausSize = str(StyleHausSize).strip()
    UrbanThreadSize = str(UrbanThreadSize).strip()

    if (
        not StyleHausSize
        or not UrbanThreadSize
    ):
        return UNKNOWN

    # Check original exact equality
    if StyleHausSize == UrbanThreadSize:
        return EXACT_MATCH

    # Normalize sizes
    StyleHausNormalizedSize = NormalizeSize(
        StyleHausSize
    )

    UrbanThreadNormalizedSize = NormalizeSize(
        UrbanThreadSize
    )

    # Check normalized equality
    if StyleHausNormalizedSize == UrbanThreadNormalizedSize:
        return NORMALIZED_MATCH

    # Different sizes or sizing systems require further verification
    return UNKNOWN

def NormalizeMaterial(Material):

    if Material is None:
        return None

    Material = str(Material).strip().lower()

    if not Material:
        return None

    # Normalize common separators
    Material = re.sub(r"[/,&+]", " ", Material)

    # Replace remaining punctuation with spaces
    Material = re.sub(r"[^a-z0-9\s]", " ", Material)

    # Normalize whitespace
    Material = re.sub(r"\s+", " ", Material).strip()

    # Sort tokens to handle different material ordering
    MaterialTokens = sorted(Material.split())

    return " ".join(MaterialTokens)

def VerifyMaterial(
    StyleHausMaterial,
    UrbanThreadMaterial
):

    # Handle missing values
    if (
        StyleHausMaterial is None
        or UrbanThreadMaterial is None
    ):
        return UNKNOWN

    StyleHausMaterial = str(StyleHausMaterial).strip()
    UrbanThreadMaterial = str(UrbanThreadMaterial).strip()

    if (
        not StyleHausMaterial
        or not UrbanThreadMaterial
    ):
        return UNKNOWN

    # Check original exact equality
    if StyleHausMaterial == UrbanThreadMaterial:
        return EXACT_MATCH

    # Normalize material descriptions
    StyleHausNormalizedMaterial = NormalizeMaterial(
        StyleHausMaterial
    )

    UrbanThreadNormalizedMaterial = NormalizeMaterial(
        UrbanThreadMaterial
    )

    # Check normalized equality
    if StyleHausNormalizedMaterial == UrbanThreadNormalizedMaterial:
        return NORMALIZED_MATCH

    # Different material descriptions require further verification
    return UNKNOWN