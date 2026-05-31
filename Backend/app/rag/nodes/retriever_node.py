from app.services.embedder import EmbeddingService
from app.services.qdrant_store import QdrantStore
from app.rag.state import ChatState

# Initialize services at module level to reuse across invocations
embedder = EmbeddingService()
store = QdrantStore()

def retriever_node(state: ChatState) -> ChatState:
    question = state["question"]
    
    query_embedding = embedder.embed(question)
    
    results = store.search(query_embedding, limit=3)
    
    # Extract payload from Qdrant PointStruct results
    state["retrieved_chunks"] = [r.payload for r in results]
    
    return state
