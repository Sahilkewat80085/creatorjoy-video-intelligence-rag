import sys
import os
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

from app.services.embedder import EmbeddingService
from app.services.qdrant_store import QdrantStore

query = "What is this song about? Is it about love and relationship and feeling?"
print(f"Query: '{query}'")

print("Initializing services...")
embedder = EmbeddingService()
store = QdrantStore()

print("Embedding query...")
query_embedding = embedder.embed(query)

print("Searching Qdrant...")
results = store.search(query_embedding, limit=3)

print("\n--- Top Results ---")
for i, result in enumerate(results):
    print(f"\nResult {i+1} (Score: {result.score:.4f}):")
    print(result.payload.get('text', 'No text found'))
