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

    # Normalize known joined model-name tokens.
    ProductName = re.sub(r"\bairmax\b", "air max", ProductName)
    ProductName = re.sub(r"\bairforce\b", "air force", ProductName)

    # Normalize common catalog abbreviations as whole tokens.
    ProductNameAliases = {
        "wht": "white",
        "blk": "black",
        "gry": "gray",
        "grey": "gray",
        "grn": "green",
        "blu": "blue"
    }

    # Preserve letters and model numbers; replace punctuation with spaces.
    ProductName = re.sub(r"[^a-z0-9\s]", " ", ProductName)
    ProductNameTokens = ProductName.split()

    ProductNameTokens = [
        ProductNameAliases.get(Token, Token)
        for Token in ProductNameTokens
    ]

    return " ".join(ProductNameTokens)

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

    # Remove known retailer/product-line qualifier when used as a prefix.
    Color = re.sub(r"^tnf\s+", "", Color)

    # Normalize spelling and common catalog color aliases.
    Color = re.sub(r"\bgrey\b", "gray", Color)
    Color = re.sub(r"\bnavy\s+blue\b", "navy", Color)

    ColorAliases = {
        "wht": "white",
        "blk": "black",
        "gry": "gray",
        "blu": "blue"
    }

    Color = re.sub(r"[^a-z0-9\s]", " ", Color)
    Tokens = [
        ColorAliases.get(Token, Token)
        for Token in Color.split()
    ]

    # Sorting is safe for compound color descriptions, but does not
    # collapse descriptive terms such as "stonewash" into "wash".
    return " ".join(sorted(Tokens))

def VerifyColor(
    StyleHausColor,
    UrbanThreadColor
):

    if (
        StyleHausColor is None
        or UrbanThreadColor is None
    ):
        return UNKNOWN

    StyleHausColor = str(StyleHausColor).strip()
    UrbanThreadColor = str(UrbanThreadColor).strip()

    if not StyleHausColor or not UrbanThreadColor:
        return UNKNOWN

    if StyleHausColor == UrbanThreadColor:
        return EXACT_MATCH

    StyleHausNormalizedColor = NormalizeColor(StyleHausColor)
    UrbanThreadNormalizedColor = NormalizeColor(UrbanThreadColor)

    if StyleHausNormalizedColor == UrbanThreadNormalizedColor:
        return NORMALIZED_MATCH

    # Only declare a mismatch when both values consist exclusively
    # of recognized color terms. Descriptive finishes such as
    # "stonewash" remain UNKNOWN for further review.
    KnownColorTokens = {
        "black", "white", "gray", "blue", "navy",
        "red", "green", "yellow", "orange", "pink",
        "purple", "brown", "beige", "cream", "silver",
        "gold", "tan", "khaki", "maroon", "olive"
    }

    StyleHausTokens = set(StyleHausNormalizedColor.split())
    UrbanThreadTokens = set(UrbanThreadNormalizedColor.split())

    if (
        StyleHausTokens
        and UrbanThreadTokens
        and StyleHausTokens.issubset(KnownColorTokens)
        and UrbanThreadTokens.issubset(KnownColorTokens)
    ):
        return MISMATCH

    return UNKNOWN

def NormalizeSize(Size):

    if Size is None:
        return None

    Size = str(Size).strip().lower()

    if not Size:
        return None

    Size = re.sub(r"\s+", " ", Size).strip()

    # Standardize common apparel-size descriptions.
    SizeAliases = {
        "extra small": "xs",
        "x small": "xs",
        "small": "s",
        "medium": "m",
        "large": "l",
        "extra large": "xl",
        "x large": "xl",
        "extra extra large": "xxl",
        "2xl": "xxl",
        "3xl": "xxxl"
    }

    if Size in SizeAliases:
        return SizeAliases[Size]

    # Standardize recognized system prefixes without converting
    # between systems (US, UK and EU are not interchangeable).
    Size = re.sub(
        r"\b(us|uk|eu)\s*(?=\d)",
        r"\1 ",
        Size
    )

    # A bare numeric size and an explicitly US-prefixed numeric size
    # are treated as equivalent in this catalog's footwear examples.
    Size = re.sub(r"^us\s+(?=\d)", "", Size)

    return re.sub(r"\s+", " ", Size).strip()

def VerifySize(
    StyleHausSize,
    UrbanThreadSize
):

    if StyleHausSize is None or UrbanThreadSize is None:
        return UNKNOWN

    StyleHausSize = str(StyleHausSize).strip()
    UrbanThreadSize = str(UrbanThreadSize).strip()

    if not StyleHausSize or not UrbanThreadSize:
        return UNKNOWN

    if StyleHausSize == UrbanThreadSize:
        return EXACT_MATCH

    StyleHausNormalizedSize = NormalizeSize(StyleHausSize)
    UrbanThreadNormalizedSize = NormalizeSize(UrbanThreadSize)

    if StyleHausNormalizedSize == UrbanThreadNormalizedSize:
        return NORMALIZED_MATCH

    # Do not compare explicit, different sizing systems as if they
    # represented the same scale.
    HasDifferentExplicitSystems = (
        re.match(r"^(uk|eu)\s", StyleHausNormalizedSize)
        and re.match(r"^(uk|eu)\s", UrbanThreadNormalizedSize)
        and StyleHausNormalizedSize.split()[0]
            != UrbanThreadNormalizedSize.split()[0]
    )

    if HasDifferentExplicitSystems:
        return UNKNOWN

    # If both values are numeric (or numeric with the same explicit
    # system), a different number is a confirmed size mismatch.
    NumericPattern = r"^(?:(uk|eu)\s+)?(\d+(?:\.\d+)?)$"
    StyleHausMatch = re.match(NumericPattern, StyleHausNormalizedSize)
    UrbanThreadMatch = re.match(NumericPattern, UrbanThreadNormalizedSize)

    if StyleHausMatch and UrbanThreadMatch:
        StyleHausSystem = StyleHausMatch.group(1)
        UrbanThreadSystem = UrbanThreadMatch.group(1)

        if StyleHausSystem == UrbanThreadSystem:
            return MISMATCH

    # Different or ambiguous size formats require review.
    return UNKNOWN

def NormalizeMaterial(Material):

    if Material is None:
        return None

    Material = str(Material).strip().lower()

    if not Material:
        return None

    # Treat separators consistently.
    Material = re.sub(r"[/,&+]", " ", Material)
    Material = re.sub(r"[^a-z0-9\s]", " ", Material)
    Material = re.sub(r"\s+", " ", Material).strip()

    # "upper" is a descriptive product-construction suffix, not a
    # separate material. Remove it only as a standalone trailing token.
    Material = re.sub(r"\bupper\b", "", Material)
    Material = re.sub(r"\s+", " ", Material).strip()

    # Sort tokens so equivalent material lists in different orders match.
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