import numpy as np


def CalculateCosineSimilarity(VectorA, VectorB):

    # Convert embeddings into NumPy arrays
    VectorA = np.asarray(VectorA, dtype=np.float64)
    VectorB = np.asarray(VectorB, dtype=np.float64)

    # Validate dimensions
    if VectorA.ndim != 1 or VectorB.ndim != 1:
        raise ValueError("Embeddings must be one-dimensional vectors.")

    if VectorA.shape != VectorB.shape:
        raise ValueError(
            f"Embedding dimension mismatch: "
            f"{VectorA.shape} vs {VectorB.shape}"
        )

    # Validate numerical values
    if not np.all(np.isfinite(VectorA)):
        raise ValueError("VectorA contains invalid numerical values.")

    if not np.all(np.isfinite(VectorB)):
        raise ValueError("VectorB contains invalid numerical values.")

    # Calculate vector magnitudes
    MagnitudeA = np.linalg.norm(VectorA)
    MagnitudeB = np.linalg.norm(VectorB)

    # Prevent division by zero
    if MagnitudeA == 0 or MagnitudeB == 0:
        raise ValueError("Cannot calculate cosine similarity for zero vectors.")

    # Calculate cosine similarity
    Similarity = np.dot(VectorA, VectorB) / (
        MagnitudeA * MagnitudeB
    )

    return float(Similarity)