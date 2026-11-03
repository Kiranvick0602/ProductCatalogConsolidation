# ============================================================
# ATTRIBUTE VERIFICATION OUTCOMES
# ============================================================

EXACT_MATCH = "EXACT_MATCH"

NORMALIZED_MATCH = "NORMALIZED_MATCH"

PARTIAL_MATCH = "PARTIAL_MATCH"

MISMATCH = "MISMATCH"

UNKNOWN = "UNKNOWN"


# ============================================================
# ATTRIBUTE COMPARISON RULES
# ============================================================

ATTRIBUTE_RULES = {

    "Brand": {
        "SourceColumns": [
            "StyleHaus_Brand",
            "UrbanThread_Brand"
        ],
        "NormalizationColumns": [
            "CanonicalBrand"
        ],
        "ComparisonType": "CANONICAL_EQUALITY",
        "IdentityAttribute": True
    },

    "ProductName": {
        "SourceColumns": [
            "StyleHaus_ProductName",
            "UrbanThread_ProductName"
        ],
        "NormalizationColumns": [
            "StyleHaus_NormalizedProductName",
            "UrbanThread_NormalizedProductName"
        ],
        "ExistingSignals": [
            "ProductNameExactMatch",
            "ProductNameSimilarity"
        ],
        "ComparisonType": "NAME_AND_MODEL_COMPARISON",
        "IdentityAttribute": True
    },

    "Category": {
        "SourceColumns": [
            "StyleHaus_Category",
            "UrbanThread_Category"
        ],
        "NormalizationColumns": [
            "StyleHaus_NormalizedCategory",
            "UrbanThread_NormalizedCategory"
        ],
        "ExistingSignals": [
            "CategoryMatch"
        ],
        "ComparisonType": "NORMALIZED_EQUALITY",
        "IdentityAttribute": True
    },

    "Color": {
        "SourceColumns": [
            "StyleHaus_Color",
            "UrbanThread_Color"
        ],
        "NormalizationColumns": [
            "StyleHaus_NormalizedColor",
            "UrbanThread_NormalizedColor"
        ],
        "ExistingSignals": [
            "ColorMatch"
        ],
        "ComparisonType": "COLOR_COMPONENT_COMPARISON",
        "IdentityAttribute": True
    },

    "Size": {
        "SourceColumns": [
            "StyleHaus_Size",
            "UrbanThread_Size"
        ],
        "NormalizationColumns": [
            "StyleHaus_NormalizedSize",
            "UrbanThread_NormalizedSize"
        ],
        "ExistingSignals": [
            "SizeMatch"
        ],
        "ComparisonType": "SIZE_SYSTEM_AWARE_COMPARISON",
        "IdentityAttribute": True
    },

    "Material": {
        "SourceColumns": [
            "StyleHaus_Material",
            "UrbanThread_Material"
        ],
        "NormalizationColumns": [
            "StyleHaus_NormalizedMaterial",
            "UrbanThread_NormalizedMaterial"
        ],
        "ExistingSignals": [
            "MaterialMatch"
        ],
        "ComparisonType": "MATERIAL_COMPONENT_COMPARISON",
        "IdentityAttribute": True
    },

    "Description": {
        "SourceColumns": [
            "StyleHaus_Description",
            "UrbanThread_Description"
        ],
        "NormalizationColumns": [
            "StyleHaus_NormalizedDescription",
            "UrbanThread_NormalizedDescription"
        ],
        "ExistingSignals": [
            "DescriptionSimilarity"
        ],
        "ComparisonType": "SEMANTIC_SIMILARITY",
        "IdentityAttribute": False
    },

    "Price": {
        "SourceColumns": [
            "StyleHaus_Price",
            "UrbanThread_Price"
        ],
        "ExistingSignals": [
            "PriceDifference",
            "PriceDifferencePct"
        ],
        "ComparisonType": "NUMERIC_DIFFERENCE",
        "IdentityAttribute": False
    },

    "Stock": {
        "SourceColumns": [
            "StyleHaus_InStock",
            "UrbanThread_InStock"
        ],
        "ComparisonType": "AVAILABILITY_COMPARISON",
        "IdentityAttribute": False
    }

}


# ============================================================
# GENERAL VERIFICATION CONFIGURATION
# ============================================================

VERIFICATION_OUTCOMES = [
    EXACT_MATCH,
    NORMALIZED_MATCH,
    PARTIAL_MATCH,
    MISMATCH,
    UNKNOWN
]


# ============================================================
# EXCLUDED FROM PRODUCT IDENTITY
# ============================================================

NON_IDENTITY_ATTRIBUTES = [
    "Description",
    "Price",
    "Stock"
]