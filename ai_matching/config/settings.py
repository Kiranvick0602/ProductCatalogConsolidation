"""
Centralized Configuration and Settings for ProductCatalogConsolidation.
Reads from environment variables with fallback defaults.
"""
import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

# Optional .env loading
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    except Exception:
        pass


# ==================================================
# LM STUDIO CONFIGURATION
# ==================================================

LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")

LM_STUDIO_MODELS_ENDPOINT = os.getenv(
    "LM_STUDIO_MODELS_ENDPOINT",
    f"{LM_STUDIO_BASE_URL}/models"
)

LM_STUDIO_EMBEDDINGS_ENDPOINT = os.getenv(
    "LM_STUDIO_EMBEDDINGS_ENDPOINT",
    f"{LM_STUDIO_BASE_URL}/embeddings"
)

LM_STUDIO_CHAT_ENDPOINT = os.getenv(
    "LM_STUDIO_CHAT_ENDPOINT",
    f"{LM_STUDIO_BASE_URL}/chat/completions"
)


# ==================================================
# MODEL CONFIGURATION
# ==================================================

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "text-embedding-nomic-embed-text-v1.5"
)

LLM_MODEL_NAME = os.getenv(
    "LLM_MODEL_NAME",
    "phi-3-mini-4k-instruct"
)


# ==================================================
# EMBEDDING CONFIGURATION
# ==================================================

EMBEDDING_TASK_PREFIX = os.getenv("EMBEDDING_TASK_PREFIX", "classification: ")

EMBEDDING_TIMEOUT = int(os.getenv("EMBEDDING_TIMEOUT", "120"))


# ==================================================
# REQUEST CONFIGURATION
# ==================================================

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))
