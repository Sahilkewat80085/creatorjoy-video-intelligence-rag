import os
import logging
from typing import Optional
import google.generativeai as genai
from app.services.embedder import EmbeddingService
from app.services.qdrant_store import QdrantStore

logger = logging.getLogger(__name__)


class SimpleRAGPipeline:
    def __init__(self):
        """
        Initializes the SimpleRAGPipeline, loading dependencies (embedder, vector store)
        and configuring the generative model.
        
        Raises:
            ValueError: If the GEMINI_API_KEY environment variable is not set.
            RuntimeError: If dependency initialization or model configuration fails.
        """
        logger.info("Initializing SimpleRAGPipeline...")
        try:
            self.embedder = EmbeddingService()
            self.store = QdrantStore()
        except Exception as e:
            logger.exception("Failed to initialize embedder or vector store dependencies.")
            raise RuntimeError("Pipeline dependencies initialization failed.") from e
        
        gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not gemini_api_key:
            err_msg = "GEMINI_API_KEY is not set in environment variables."
            logger.error(err_msg)
            raise ValueError(err_msg)
            
        try:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("Generative model configured successfully.")
        except Exception as e:
            logger.exception("Failed to configure Gemini model in SimpleRAGPipeline.")
            raise RuntimeError("Generative model configuration failed.") from e

    def ask(self, question: str) -> str:
        """
        Executes a simple Retrieval-Augmented Generation (RAG) query.
        Embeds the question, retrieves relevant documents, and asks the model to generate an answer.
        
        Args:
            question: The user query string.
            
        Returns:
            The generated response string.
            
        Raises:
            ValueError: If the query string is empty.
            RuntimeError: If query execution, retrieval, or generation fails.
        """
        if not question or not isinstance(question, str):
            err_msg = "Query question must be a non-empty string."
            logger.error(err_msg)
            raise ValueError(err_msg)
            
        logger.info("Processing RAG query: '%s'", question)
        
        try:
            # 1. Embed Query
            logger.info("Generating embedding for query...")
            query_embedding = self.embedder.embed(question)
            
            # 2. Retrieve Chunks
            logger.info("Searching vector database for matching chunks...")
            results = self.store.search(query_embedding, limit=3)
            context_text = "\n\n".join([r.payload.get('text', '') for r in results if r.payload])
            
            # 3. Build Prompt
            prompt = f"""You are a creator intelligence assistant.

Context:
{context_text}

Question:
{question}

Answer using only the provided context."""

            # 4. Generate response
            logger.info("Calling generative model to generate response...")
            response = self.model.generate_content(prompt)
            logger.info("Response successfully generated.")
            return response.text
        except Exception as e:
            logger.exception("Failed to execute RAG query workflow.")
            raise RuntimeError(f"RAG query failed: {str(e)}") from e

