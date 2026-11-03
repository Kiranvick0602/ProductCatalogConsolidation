# ==============================================================================
# PRODUCT MATCH DECISION RULES - EXACT PRODUCT VARIANT MATCHING
# ==============================================================================

# These attributes determine whether two records represent the same variant.
REQUIRED_IDENTITY_ATTRIBUTES = {
    "Brand": "VerifiedBrandMatch",
    "ProductName": "VerifiedProductNameMatch",
    "Category": "VerifiedCategoryMatch",
    "Color": "VerifiedColorMatch",
    "Size": "VerifiedSizeMatch",
}

# Material is supporting evidence only. A material difference alone does not
# prove that the product variant is different under the agreed project rules.
SUPPORTING_ATTRIBUTES = {
    "Material": "VerifiedMaterialMatch",
}

MATCH_STATUSES = {"EXACT_MATCH", "NORMALIZED_MATCH"}


def EvaluateMatchDecision(Candidate):
    MatchedAttributes = []
    UnknownAttributes = []
    MismatchedAttributes = []
    SupportingMatchAttributes = []
    SupportingUnknownAttributes = []
    SupportingMismatchAttributes = []

    for AttributeName, VerificationColumn in REQUIRED_IDENTITY_ATTRIBUTES.items():
        VerificationResult = Candidate.get(VerificationColumn)
        if VerificationResult in MATCH_STATUSES:
            MatchedAttributes.append(AttributeName)
        elif VerificationResult == "MISMATCH":
            MismatchedAttributes.append(AttributeName)
        else:
            UnknownAttributes.append(AttributeName)

    for AttributeName, VerificationColumn in SUPPORTING_ATTRIBUTES.items():
        VerificationResult = Candidate.get(VerificationColumn)
        if VerificationResult in MATCH_STATUSES:
            SupportingMatchAttributes.append(AttributeName)
        elif VerificationResult == "MISMATCH":
            SupportingMismatchAttributes.append(AttributeName)
        else:
            SupportingUnknownAttributes.append(AttributeName)

    if MismatchedAttributes:
        FinalDecision = "NO_MATCH"
    elif not UnknownAttributes:
        FinalDecision = "MATCH"
    else:
        FinalDecision = "REVIEW"

    return {
        "RuleBasedDecision": FinalDecision,
        "MatchedAttributes": MatchedAttributes,
        "UnknownAttributes": UnknownAttributes,
        "MismatchedAttributes": MismatchedAttributes,
        "SupportingMatchAttributes": SupportingMatchAttributes,
        "SupportingUnknownAttributes": SupportingUnknownAttributes,
        "SupportingMismatchAttributes": SupportingMismatchAttributes,
    }
