"""Local semantic embeddings, with no hosted inference API."""

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"


class LocalEmbedder:
    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(MODEL_ID)

    def matrix(self, source_units: list[str], chunk_texts: list[str]) -> list[list[float]]:
        import numpy as np

        source_vectors = self.model.encode(source_units, normalize_embeddings=True, show_progress_bar=False)
        chunk_vectors = self.model.encode(chunk_texts, normalize_embeddings=True, show_progress_bar=False)
        return np.matmul(source_vectors, chunk_vectors.T).tolist()
