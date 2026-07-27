import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    _instance: Optional['EmbeddingService'] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls) -> 'EmbeddingService':
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the EmbeddingService singleton.
        """
        pass

    @property
    def model(self) -> SentenceTransformer:
        """
        Retrieves or initializes the SentenceTransformer model instance.
        
        Returns:
            The loaded SentenceTransformer model.
            
        Raises:
            RuntimeError: If the model fails to load.
        """
        if EmbeddingService._model is None:
            logger.info("Loading SentenceTransformer model 'BAAI/bge-small-en-v1.5'...")
            try:
                EmbeddingService._model = SentenceTransformer("BAAI/bge-small-en-v1.5")
                logger.info("SentenceTransformer model successfully loaded.")
            except Exception as e:
                logger.exception("Failed to load SentenceTransformer model 'BAAI/bge-small-en-v1.5'.")
                raise RuntimeError("Failed to load sentence-transformers model.") from e
        return EmbeddingService._model

    def embed(self, text: str) -> List[float]:
        """
        Embeds a single string and returns it as a list of floats.
        
        Args:
            text: The input string to embed.
            
        Returns:
            A list of floats representing the embedding vector.
            
        Raises:
            ValueError: If input text is invalid.
            RuntimeError: If embedding model execution fails.
        """
        if not text or not isinstance(text, str):
            err_msg = "Input text to embed must be a non-empty string."
            logger.error(err_msg)
            raise ValueError(err_msg)

        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.exception("Failed to generate embedding for input text.")
            raise RuntimeError("Embedding generation failed.") from e
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of strings and returns a list of embeddings.
        
        Args:
            texts: A list of input strings.
            
        Returns:
            A list of lists of floats representing the embedding vectors.
            
        Raises:
            ValueError: If input texts list is invalid.
            RuntimeError: If embedding model execution fails.
        """
        if not isinstance(texts, list):
            err_msg = "Input texts to embed_batch must be a list of strings."
            logger.error(err_msg)
            raise ValueError(err_msg)
            
        for i, text in enumerate(texts):
            if not text or not isinstance(text, str):
                err_msg = f"Element at index {i} in texts list must be a non-empty string."
                logger.error(err_msg)
                raise ValueError(err_msg)

        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.exception("Failed to generate batch embeddings.")
            raise RuntimeError("Batch embedding generation failed.") from e

