"""
Phase 5.7 - Phi-3 validation for unresolved product candidate pairs.

Reads CandidatePairs_FinalMatchingDecisions.csv, sends ONLY rows whose
FinalMatchDecision == REVIEW to LM Studio, and writes an auditable result.
The existing FinalMatchDecision is never overwritten by this script.
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ProjectRoot = Path(__file__).resolve().parents[2]
InputPath = ProjectRoot / "data" / "output" / "CandidatePairs_FinalMatchingDecisions.csv"
OutputDir = ProjectRoot / "data" / "output" / "quality" / "phi3_validation"
OutputCsvPath = OutputDir / "CandidatePairs_Phi3Validation.csv"
OutputJsonlPath = OutputDir / "Phi3Validation_Responses.jsonl"

LMStudioChatEndpoint = "http://localhost:1234/v1/chat/completions"
ModelName = "phi-3-mini-4k-instruct"
RequestTimeoutSeconds = 120
MaxRetries = 3
RetryDelaySeconds = 2
Temperature = 0.0
MaxTokens = 300


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def GetValue(Candidate, ColumnName):
    Value = Candidate.get(ColumnName)
    if pd.isna(Value) or str(Value).strip() == "":
        return "Not Available"
    return str(Value).strip()


def BuildProductMatchingPrompt(Candidate):
    ProductAttributes = [
        "ProductName",
        "Brand",
        "Category",
        "Description",
        "Color",
        "Size",
        "Material",
        "Price",
    ]

    StyleHausProduct = {
        Attribute: GetValue(Candidate, f"StyleHaus_{Attribute}")
        for Attribute in ProductAttributes
    }
    UrbanThreadProduct = {
        Attribute: GetValue(Candidate, f"UrbanThread_{Attribute}")
        for Attribute in ProductAttributes
    }

    ExistingVerification = {
        "VerifiedBrandMatch": GetValue(Candidate, "VerifiedBrandMatch"),
        "VerifiedProductModelMatch_V4_3_1": GetValue(
            Candidate, "VerifiedProductModelMatch_V4_3_1"
        ),
        "VerifiedColorMatch_V3_1": GetValue(
            Candidate, "VerifiedColorMatch_V3_1"
        ),
        "FinalVerifiedSizeMatch": GetValue(
            Candidate, "FinalVerifiedSizeMatch"
        ),
        "EmbeddingSimilarity": GetValue(Candidate, "EmbeddingSimilarity"),
        "CurrentFinalDecision": GetValue(Candidate, "FinalMatchDecision"),
        "CurrentDecisionReason": GetValue(Candidate, "DecisionReason"),
    }

    return f"""
You are validating an ambiguous cross-retailer product pair.

Determine whether the two records represent the SAME exact sellable
product variant, not merely similar products or the same product family.

STYLEHAUS PRODUCT:
{json.dumps(StyleHausProduct, ensure_ascii=False, indent=2)}

URBANTHREAD PRODUCT:
{json.dumps(UrbanThreadProduct, ensure_ascii=False, indent=2)}

EXISTING DETERMINISTIC VERIFICATION:
{json.dumps(ExistingVerification, ensure_ascii=False, indent=2)}

RULES:
1. A different product model or product type means NO_MATCH.
2. Exact product variant matters. Different colors or sizes mean NO_MATCH.
3. Similar base colors do not prove identical shades/finishes. For example,
   "Spruce Green" and "Green", "Stonewash Grey" and "Grey", or "Black Smooth"
   and "Black" may be related, but the supplied data may not prove they are
   the same exact catalog variant. If uncertain, choose REVIEW.
4. A more specific color/material description is not automatically a
   contradiction, but do not assume equivalence without evidence.
5. Treat size labels such as "10" and "US 10" as equivalent only when they
   clearly represent the same sizing system/value.
6. Brand, category, material, descriptions, price, and embedding similarity
   are supporting evidence. None independently proves identity.
7. Do not invent SKU/model details, color equivalences, or product facts.
8. The deterministic pipeline currently marked this pair REVIEW. Your output
   is validation evidence only; it does not authorize automatic merging.
9. Prefer REVIEW whenever the available fields cannot establish exact
   variant identity.

Return ONLY one valid JSON object with exactly these fields:
{{
  "IsMatch": true,
  "Confidence": 0.95,
  "Reason": "Short explanation based only on supplied evidence."
}}

IsMatch must be true, false, or null.
Confidence must be a number from 0 to 1, or null when IsMatch is null.
Reason must be a non-empty string.
""".strip()


# ---------------------------------------------------------------------------
# Response parsing and validation
# ---------------------------------------------------------------------------

def ParseModelResponse(ResponseText):
    Text = ResponseText.strip()
    Text = re.sub(r"^```(?:json)?\s*", "", Text, flags=re.IGNORECASE)
    Text = re.sub(r"\s*```$", "", Text)

    Start = Text.find("{")
    End = Text.rfind("}")
    if Start < 0 or End < Start:
        raise ValueError("No JSON object found in model response.")

    Payload = json.loads(Text[Start : End + 1])

    RequiredFields = {"IsMatch", "Confidence", "Reason"}
    if set(Payload.keys()) != RequiredFields:
        raise ValueError("Response must contain exactly IsMatch, Confidence, Reason.")

    IsMatch = Payload["IsMatch"]
    Confidence = Payload["Confidence"]
    Reason = Payload["Reason"]

    if IsMatch is not True and IsMatch is not False and IsMatch is not None:
        raise ValueError("IsMatch must be true, false, or null.")

    if Confidence is not None:
        if isinstance(Confidence, bool) or not isinstance(Confidence, (int, float)):
            raise ValueError("Confidence must be numeric or null.")
        if not 0.0 <= float(Confidence) <= 1.0:
            raise ValueError("Confidence must be between 0 and 1.")

    if IsMatch is None and Confidence is not None:
        # Confidence for an unresolved response is allowed, but the model
        # should not imply a decisive probability. Keep the value as supplied.
        pass
    elif IsMatch is not None and Confidence is None:
        raise ValueError("Confidence is required for a decisive response.")

    if not isinstance(Reason, str) or not Reason.strip():
        raise ValueError("Reason must be a non-empty string.")

    Decision = "MATCH" if IsMatch is True else "NO_MATCH" if IsMatch is False else "REVIEW"

    return {
        "Phi3IsMatch": IsMatch,
        "Phi3ValidationDecision": Decision,
        "Phi3Confidence": float(Confidence) if Confidence is not None else None,
        "Phi3Reason": Reason.strip(),
        "Phi3ResponseValid": True,
    }


def CallPhi3(Candidate, Session):
    Payload = {
        "model": ModelName,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a conservative product identity validator. "
                    "Return only a valid JSON object."
                ),
            },
            {
                "role": "user",
                "content": BuildProductMatchingPrompt(Candidate),
            },
        ],
        "temperature": 0.0,
        "max_tokens": 300,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "product_matching_validation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "IsMatch": {
                            "type": ["boolean", "null"]
                        },
                        "Confidence": {
                            "type": ["number", "null"]
                        },
                        "Reason": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "IsMatch",
                        "Confidence",
                        "Reason"
                    ],
                    "additionalProperties": False
                }
            }
        },
    }

    LastError = None
    LastRawResponse = None

    for Attempt in range(1, MaxRetries + 1):

        AttemptRecord = {
            "CandidatePairID": Candidate.get("CandidatePairID"),
            "Attempt": Attempt,
            "ModelName": ModelName,
            "TimestampUtc": datetime.now(timezone.utc).isoformat(),
        }

        try:
            Response = Session.post(
                LMStudioChatEndpoint,
                json=Payload,
                timeout=RequestTimeoutSeconds,
            )

            # Capture HTTP response BEFORE parsing
            LastRawResponse = Response.text

            AttemptRecord["HttpStatusCode"] = Response.status_code
            AttemptRecord["HttpResponseBody"] = Response.text

            Response.raise_for_status()

            ResponseJson = Response.json()

            Message = ResponseJson["choices"][0]["message"]
            ResponseText = Message.get("content")

            if not isinstance(ResponseText, str):
                raise ValueError(
                    f"Unexpected response content: {type(ResponseText).__name__}"
                )

            LastRawResponse = ResponseText
            AttemptRecord["ModelResponse"] = ResponseText

            # Parse model response
            Result = ParseModelResponse(ResponseText)

            AttemptRecord["ParseValid"] = True
            AttemptRecord["ParseError"] = None

            AppendJsonl(AttemptRecord)

            Result.update({
                "Phi3ModelName": ModelName,
                "Phi3AttemptCount": Attempt,
                "Phi3RawResponse": ResponseText,
                "Phi3LastError": None,
            })

            return Result

        except (
            requests.RequestException,
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as Error:

            LastError = str(Error)

            AttemptRecord["ModelResponse"] = LastRawResponse
            AttemptRecord["ParseValid"] = False
            AttemptRecord["ParseError"] = LastError

            AppendJsonl(AttemptRecord)

            print(f"    Attempt {Attempt} failed: {LastError}")

            if Attempt < MaxRetries:
                time.sleep(RetryDelaySeconds * Attempt)

    return {
        "Phi3IsMatch": None,
        "Phi3ValidationDecision": "REVIEW",
        "Phi3Confidence": None,
        "Phi3Reason": f"Phi-3 failed after {MaxRetries} attempts: {LastError}",
        "Phi3ResponseValid": False,
        "Phi3ModelName": ModelName,
        "Phi3AttemptCount": MaxRetries,
        "Phi3RawResponse": LastRawResponse,
        "Phi3LastError": LastError,
    }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def AppendJsonl(Record):
    with OutputJsonlPath.open("a", encoding="utf-8") as File:
        File.write(json.dumps(Record, ensure_ascii=False, default=str) + "\n")


def main():
    if not InputPath.exists():
        raise FileNotFoundError(
            f"Input file not found: {InputPath}\n"
            "Place CandidatePairs_FinalMatchingDecisions.csv in data/output/."
        )

    OutputDir.mkdir(parents=True, exist_ok=True)
    OutputJsonlPath.write_text("", encoding="utf-8")

    CandidatePairsDf = pd.read_csv(InputPath)
    ReviewDf = CandidatePairsDf[
        CandidatePairsDf["FinalMatchDecision"].astype(str).str.upper().eq("REVIEW")
    ].copy()

    if ReviewDf.empty:
        print("No REVIEW records found. Nothing to send to Phi-3.")
        return

    print(f"Total candidate pairs: {len(CandidatePairsDf)}")
    print(f"REVIEW records to validate: {len(ReviewDf)}")
    print(f"Model: {ModelName}")
    print(f"LM Studio endpoint: {LMStudioChatEndpoint}")

    # Verify LM Studio is reachable before starting any inference.
    try:
        HealthResponse = requests.get(
            "http://localhost:1234/v1/models",
            timeout=10,
        )
        HealthResponse.raise_for_status()
        print("LM Studio connection: OK")
    except requests.RequestException as Error:
        raise RuntimeError(
            "Cannot reach LM Studio at http://localhost:1234. "
            "Start the LM Studio local server and load Phi-3 Mini Instruct."
        ) from Error

    Results = []
    with requests.Session() as Session:
        for Index, (_, Candidate) in enumerate(ReviewDf.iterrows(), start=1):
            CandidateRecord = Candidate.to_dict()
            print(
                f"[{Index}/{len(ReviewDf)}] "
                f"{CandidateRecord.get('StyleHaus_ProductName')} "
                f"<-> {CandidateRecord.get('UrbanThread_ProductName')}"
            )

            Phi3Result = CallPhi3(CandidateRecord, Session)
            ProcessedAt = datetime.now(timezone.utc).isoformat()

            ResultRecord = {
                "CandidatePairID": CandidateRecord.get("CandidatePairID"),
                "StyleHaus_ProductID": CandidateRecord.get("StyleHaus_ProductID"),
                "UrbanThread_ProductID": CandidateRecord.get("UrbanThread_ProductID"),
                "StyleHaus_ProductName": CandidateRecord.get("StyleHaus_ProductName"),
                "UrbanThread_ProductName": CandidateRecord.get("UrbanThread_ProductName"),
                "OriginalFinalMatchDecision": CandidateRecord.get("FinalMatchDecision"),
                "OriginalDecisionReason": CandidateRecord.get("DecisionReason"),
                **Phi3Result,
                "Phi3ProcessedAt": ProcessedAt,
            }

            Results.append(ResultRecord)
            AppendJsonl(ResultRecord)

            print(
                f"    Phi-3: {Phi3Result['Phi3ValidationDecision']} | "
                f"Confidence: {Phi3Result['Phi3Confidence']} | "
                f"Valid: {Phi3Result['Phi3ResponseValid']}"
            )

    ResultsDf = pd.DataFrame(Results)
    ResultsDf.to_csv(OutputCsvPath, index=False, encoding="utf-8-sig")

    print("\nPhase 5.7 validation completed.")
    print(f"Validated records: {len(ResultsDf)}")
    print("\nPhi-3 validation counts:")
    print(ResultsDf["Phi3ValidationDecision"].value_counts(dropna=False).to_string())
    print(f"\nCSV:   {OutputCsvPath}")
    print(f"JSONL: {OutputJsonlPath}")
    print("\nIMPORTANT: Original FinalMatchDecision values were not changed.")


if __name__ == "__main__":
    main()
