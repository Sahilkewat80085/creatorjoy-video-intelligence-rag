from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @property
    def model(self):
        if EmbeddingService._model is None:
            print("Loading SentenceTransformer model...")
            EmbeddingService._model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        return EmbeddingService._model

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
