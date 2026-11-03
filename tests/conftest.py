"""
Pytest configuration and global fixtures for ProductCatalogConsolidation test suite.
"""
import sys
from pathlib import Path
import pytest

# Ensure project root is at the head of sys.path for test discovery and imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "lm_studio: mark test as requiring a running LM Studio server (embeddings or chat)."
    )
    config.addinivalue_line(
        "markers",
        "regression: mark test as part of the regression test suite."
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test requiring external services."
    )
