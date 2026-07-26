import logging
from typing import List, Dict, Any
from app.services.embedder import EmbeddingService
from app.services.qdrant_store import QdrantStore
from app.rag.state import ChatState

logger = logging.getLogger(__name__)

# Initialize services at module level to reuse across invocations
try:
    embedder = EmbeddingService()
    store = QdrantStore()
except Exception as e:
    logger.exception("Failed to initialize embedder or qdrant store services in retriever_node.py.")
    embedder = None
    store = None


def deduplicate_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates a list of dictionaries in an order-preserving manner.
    """
    seen = set()
    unique_citations = []
    for c in citations:
        # Convert dictionary to a sorted tuple of key-value pairs (excluding None values for safety)
        frozen = tuple(sorted((k, v) for k, v in c.items() if v is not None))
        if frozen not in seen:
            seen.add(frozen)
            unique_citations.append(c)
    return unique_citations


def retriever_node(state: ChatState) -> ChatState:
    """
    LangGraph node that retrieves relevant document chunks from Qdrant based on the user's question.
    
    Args:
        state: The current ChatState of the workflow.
        
    Returns:
        The updated ChatState with retrieved_chunks and citations populated.
    """
    question = state.get("question", "")
    chunks: List[Dict[str, Any]] = []
    citations: List[Dict[str, Any]] = []
    
    # Initialize defaults
    state["retrieved_chunks"] = chunks
    state["citations"] = citations

    if not question:
        logger.warning("Empty question passed to retriever_node.")
        return state

    if embedder is None or store is None:
        logger.error("Embedding service or Qdrant store not initialized. Returning empty state.")
        return state

    try:
        # Embed the input question
        query_embedding = embedder.embed(question)
        
        # Search Qdrant for matching chunks
        results = store.search(query_embedding, limit=3)
        
        for r in results:
            payload = r.payload
            if not payload:
                continue
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
                
        # Deduplicate citations cleanly while keeping their relative order
        state["retrieved_chunks"] = chunks
        state["citations"] = deduplicate_citations(citations)
        
        logger.info("Successfully retrieved %d chunks and %d citations.", len(chunks), len(state["citations"]))
        
    except Exception as e:
        logger.exception("Error occurred in retriever_node execution: %s", e)
        # We degrade gracefully: ChatState is left with empty chunks/citations rather than crashing the graph
        
    return state

