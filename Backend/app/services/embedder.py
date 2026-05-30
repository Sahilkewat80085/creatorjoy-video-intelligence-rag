from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:

    def __init__(self):
        # We load the BAAI/bge-small-en-v1.5 model as requested
        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def embed(self, text: str) -> List[float]:
        """
        Embeds a single string and returns it as a list of floats.
        """
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of strings and returns a list of embeddings.
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
