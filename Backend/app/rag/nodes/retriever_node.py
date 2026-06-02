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
    
    chunks = []
    citations = []
    
    for r in results:
        payload = r.payload
        chunks.append(payload)
        
        # Transcript citation
        citations.append({
            "source": "transcript",
            "video_id": payload.get("video_id"),
            "chunk_index": payload.get("chunk_index"),
            "score": round(r.score, 4) if hasattr(r, 'score') and r.score is not None else 0.0
        })
        
        # Metadata citation
        label = payload.get("label")
        if label:
            video_letter = label.replace("Video ", "").strip()
            citations.append({
                "source": "metadata",
                "video": video_letter
            })
            
    # Deduplicate citations (since order matters less than uniqueness, list of dicts can be deduplicated safely)
    unique_citations = [dict(t) for t in {tuple(d.items()) for d in citations}]
    
    state["retrieved_chunks"] = chunks
    state["citations"] = unique_citations
    
    return state
