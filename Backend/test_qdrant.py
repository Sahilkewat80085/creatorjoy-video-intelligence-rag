from app.services.qdrant_store import QdrantStore

print("Connecting to Qdrant...")
store = QdrantStore()

print("Creating collection if it doesn't exist...")
store.create_collection()

print("Qdrant setup successful!")
