import json
import re
import time
import requests

from ai_matching.config.settings import (
    LM_STUDIO_CHAT_ENDPOINT,
    LLM_MODEL_NAME,
    REQUEST_TIMEOUT
)


# ==============================================================================
# PHI-3 LLM CLIENT CONFIGURATION
# ==============================================================================

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
TEMPERATURE = 0.0
MAX_TOKENS = 400


# ==============================================================================
# BUILD PRODUCT DETAILS
# ==============================================================================

def BuildProductDetails(Candidate, Source):

    Attributes = [
        "ProductName",
        "Brand",
        "Category",
        "Color",
        "Size",
        "Material",
        "Description",
        "Price"
    ]

    ProductDetails = {}

    for Attribute in Attributes:

        ColumnName = f"{Source}_{Attribute}"

        Value = Candidate.get(ColumnName)

        if Value is None or str(Value).strip() == "":
            Value = "Not Available"

        ProductDetails[Attribute] = str(Value).strip()

    return ProductDetails


# ==============================================================================
# BUILD LLM PROMPT
# ==============================================================================

def BuildProductMatchingPrompt(Candidate):

    StyleHausProduct = BuildProductDetails(
        Candidate,
        "StyleHaus"
    )

    UrbanThreadProduct = BuildProductDetails(
        Candidate,
        "UrbanThread"
    )

    SupportingSignals = {
        "EmbeddingSimilarity": Candidate.get("EmbeddingSimilarity"),
        "ProductNameSimilarity": Candidate.get("ProductNameSimilarity"),
        "VerifiedBrandMatch": Candidate.get("VerifiedBrandMatch"),
        "VerifiedProductNameMatch": Candidate.get("VerifiedProductNameMatch"),
        "VerifiedCategoryMatch": Candidate.get("VerifiedCategoryMatch"),
        "VerifiedColorMatch": Candidate.get("VerifiedColorMatch"),
        "VerifiedSizeMatch": Candidate.get("VerifiedSizeMatch"),
        "VerifiedMaterialMatch": Candidate.get("VerifiedMaterialMatch")
    }

    Prompt = f"""
You are an expert e-commerce product matching assistant.

Your task is to determine whether two product records from different
retailers represent the SAME underlying product.

Evaluate product identity, not just general semantic similarity.

STYLEHAUS PRODUCT:
{json.dumps(StyleHausProduct, indent=2)}

URBANTHREAD PRODUCT:
{json.dumps(UrbanThreadProduct, indent=2)}

SUPPORTING MATCHING SIGNALS:
{json.dumps(SupportingSignals, indent=2)}

BUSINESS RULES:

1. Brand:
   - Matching brands are supporting evidence only.
   - Same brand does not mean the products are identical.

2. Product Name:
   - Compare the actual product model, model number,
     product line, and style.
   - Different models must be classified as NO_MATCH.
   - Ignore capitalization and harmless formatting differences.

3. Category:
   - Products must represent compatible product types.
   - A backpack and a shoe are different products.
   - A hoodie and a t-shirt are different product types.

4. Color:
   - Compare actual color variants.
   - Different color variants must not automatically
     be classified as the same exact product.
   - Missing color information is not evidence of a match.

5. Size:
   - Compare sizes when available.
   - Do not assume that different size representations
     are equivalent without sufficient evidence.
   - Missing size information must not be treated as a match.

6. Material:
   - Use material as supporting evidence.
   - Consider differences in material composition.

7. Description:
   - Use descriptions to understand product characteristics.
   - Similar descriptions alone are insufficient evidence.

8. Price:
   - Price is supporting information only.
   - Price differences do not automatically indicate
     different products.

9. Missing Information:
   - Not Available means the attribute is unknown.
   - UNKNOWN verification outcomes do not mean MATCH
     or NO_MATCH.
   - Do not invent missing product characteristics.

10. Embedding Similarity:
    - Use embedding similarity as supporting evidence only.
    - High similarity does not prove product identity.

11. Product Variants:
    - Distinguish between different models and different variants.
    - When the available information cannot establish
      whether two variants represent the same underlying
      product, return REVIEW.

DECISION GUIDELINES:

- IsMatch = true:
  Strong evidence indicates both records represent the
  same underlying product.

- IsMatch = false:
  Strong evidence indicates different product models,
  product types, or clearly different product identities.

- IsMatch = null:
  Available information is insufficient to make
  a reliable decision.

Do not force a MATCH or NO_MATCH when evidence is insufficient.
Prefer REVIEW over an unsupported decision.

Use exactly this structure:

{{
    "IsMatch": true,
    "Confidence": 0.95,
    "Reason": "Both records represent the same product model with compatible attributes."
}}

OUTPUT VALIDATION RULES:

1. IsMatch must be true, false, or null.

2. Confidence:
   - For MATCH and NO_MATCH, return a numeric value
     between 0.0 and 1.0.
   - For REVIEW, return a numeric value between
     0.0 and 1.0, or null if confidence cannot be assessed.

3. Reason must always be a non-empty string.

4. Never omit any of the three JSON fields.
"""

    return Prompt


# ==============================================================================
# EXTRACT JSON FROM LLM RESPONSE
# ==============================================================================

def ExtractJsonResponse(ResponseText):

    ResponseText = ResponseText.strip()

    # Remove Markdown code fences if returned by the model.

    ResponseText = re.sub(
        r"^```(?:json)?\s*",
        "",
        ResponseText,
        flags=re.IGNORECASE
    )

    ResponseText = re.sub(
        r"\s*```$",
        "",
        ResponseText
    )

    # Extract JSON object.

    StartIndex = ResponseText.find("{")
    EndIndex = ResponseText.rfind("}")

    if StartIndex == -1 or EndIndex == -1:
        raise ValueError("No JSON object found in LLM response.")

    JsonText = ResponseText[StartIndex:EndIndex + 1]

    return json.loads(JsonText)


# ==============================================================================
# VALIDATE LLM RESPONSE
# ==============================================================================

def ValidateLLMResponse(ResponseText):

    try:

        ResponseJson = ExtractJsonResponse(ResponseText)

        RequiredFields = [
            "IsMatch",
            "Confidence",
            "Reason"
        ]

        for Field in RequiredFields:

            if Field not in ResponseJson:
                raise ValueError(
                    f"Missing required field: {Field}"
                )

        IsMatch = ResponseJson["IsMatch"]
        Confidence = ResponseJson["Confidence"]
        Reason = ResponseJson["Reason"]

        # Validate IsMatch.

        if IsMatch is not True and IsMatch is not False and IsMatch is not None:
            raise ValueError("Invalid IsMatch value.")

        # Validate Confidence.

        if Confidence is None:

            if IsMatch is not None:
                raise ValueError(
                    "Confidence cannot be null for MATCH or NO_MATCH."
                )

        else:

            if isinstance(Confidence, bool):
                raise ValueError("Confidence must be numeric.")

            if not isinstance(Confidence, (int, float)):
                raise ValueError("Confidence must be numeric.")

            if not 0.0 <= Confidence <= 1.0:
                raise ValueError(
                    "Confidence must be between 0 and 1."
                )

        # Validate Reason.

        if not isinstance(Reason, str) or not Reason.strip():
            raise ValueError(
                "Reason must be a non-empty string."
            )

        # Map decision.

        if IsMatch is True:
            Decision = "MATCH"

        elif IsMatch is False:
            Decision = "NO_MATCH"

        else:
            Decision = "REVIEW"

        return {
            "IsMatch": IsMatch,
            "LLMDecision": Decision,
            "Confidence": (
                float(Confidence)
                if Confidence is not None
                else None
            ),
            "Reason": Reason.strip(),
            "ResponseValid": True
        }

    except (ValueError, TypeError, json.JSONDecodeError):

        return {
            "IsMatch": None,
            "LLMDecision": "REVIEW",
            "Confidence": None,
            "Reason": "Invalid or incomplete JSON response from Phi-3.",
            "ResponseValid": False
        }

# ==============================================================================
# CALL PHI-3 THROUGH LM STUDIO
# ==============================================================================

def CallPhi3(Candidate):

    Prompt = BuildProductMatchingPrompt(Candidate)

    RequestPayload = {
        "model": LLM_MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a precise e-commerce product identity "
                    "matching assistant. Follow the requested JSON "
                    "output format strictly."
                )
            },
            {
                "role": "user",
                "content": Prompt
            }
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }

    with requests.Session() as Session:

        for Attempt in range(1, MAX_RETRIES + 1):

            try:

                Response = Session.post(
                    LM_STUDIO_CHAT_ENDPOINT,
                    json=RequestPayload,
                    timeout=REQUEST_TIMEOUT
                )

                # Log detailed LM Studio error before raising HTTPError.
                if not Response.ok:

                    print("\n========== PHI-3 REQUEST FAILED ==========")
                    print(f"HTTP Status: {Response.status_code}")
                    print(f"CandidatePairID: {Candidate.get('CandidatePairID')}")
                    print(f"LM Studio Error Response: {Response.text}")

                    print("\nRequest Payload:")
                    print(RequestPayload)

                    print("==========================================\n")

                # Retry only for rate limiting or server-side errors.

                if Response.status_code == 429 or Response.status_code >= 500:

                    Response.raise_for_status()

                # Other HTTP errors are not retried.

                Response.raise_for_status()

                ResponseJson = Response.json()

                ResponseText = (
                    ResponseJson["choices"][0]["message"]["content"]
                )

                ValidatedResponse = ValidateLLMResponse(
                    ResponseText
                )

                ValidatedResponse["ModelName"] = LLM_MODEL_NAME

                ValidatedResponse["AttemptCount"] = Attempt

                ValidatedResponse["RawResponse"] = ResponseText

                return ValidatedResponse

            except requests.exceptions.HTTPError:

                if (
                    Response.status_code < 500
                    and Response.status_code != 429
                ):
                    raise

                if Attempt == MAX_RETRIES:
                    raise

                time.sleep(
                    RETRY_DELAY_SECONDS * Attempt
                )

            except requests.exceptions.RequestException:

                if Attempt == MAX_RETRIES:
                    raise

                time.sleep(
                    RETRY_DELAY_SECONDS * Attempt
                )

    raise RuntimeError("Phi-3 request failed after maximum retries.")