import os
import google.generativeai as genai
from app.services.embedder import EmbeddingService
from app.services.qdrant_store import QdrantStore

class SimpleRAGPipeline:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.store = QdrantStore()
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
            
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def ask(self, question: str) -> str:
        # Embed Query
        query_embedding = self.embedder.embed(question)
        
        # Retrieve Chunks
        results = self.store.search(query_embedding, limit=3)
        context_text = "\n\n".join([r.payload.get('text', '') for r in results])
        
        # Build Prompt
        prompt = f"""You are a creator intelligence assistant.

Context:
{context_text}

Question:
{question}

Answer using only the provided context."""

        # Gemini
        response = self.model.generate_content(prompt)
        return response.text
