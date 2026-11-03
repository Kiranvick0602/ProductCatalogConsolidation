import sys
from pathlib import Path
import requests

ProjectRoot = Path(__file__).resolve().parents[2]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from ai_matching.config.settings import (
    LM_STUDIO_MODELS_ENDPOINT,
    REQUEST_TIMEOUT
)


def TestLMStudioConnection():

    print("=" * 60)
    print("LM STUDIO CONNECTION TEST")
    print("=" * 60)

    try:

        Response = requests.get(
            LM_STUDIO_MODELS_ENDPOINT,
            timeout=REQUEST_TIMEOUT
        )

        Response.raise_for_status()

        ModelsResponse = Response.json()

        ModelsList = ModelsResponse.get("data", [])

        print("\nConnection Status: SUCCESS")

        print("\nAvailable Models:")

        for Model in ModelsList:

            ModelName = Model.get("id")

            print(f"- {ModelName}")

        print(
            f"\nTotal Models Found: {len(ModelsList)}"
        )

        return ModelsList

    except requests.exceptions.ConnectionError:

        print("\nConnection Failed!")

        print(
            "Please verify that the LM Studio server is running."
        )

    except requests.exceptions.Timeout:

        print("\nRequest timed out.")

    except requests.exceptions.HTTPError as Error:

        print(f"\nHTTP Error: {Error}")

    except Exception as Error:

        print(f"\nUnexpected Error: {Error}")

    return []


if __name__ == "__main__":

    TestLMStudioConnection()
