import sys
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from app.services.embedder import EmbeddingService

print("Initializing EmbeddingService (this will download the model if not cached)...")
service = EmbeddingService()

test_text = "Never gonna give you up, never gonna let you down."
print(f"\nEmbedding text: '{test_text}'")

vector = service.embed(test_text)

print(f"\nVector length (dimensions): {len(vector)}")
print(f"First 5 dimensions: {vector[:5]}")
