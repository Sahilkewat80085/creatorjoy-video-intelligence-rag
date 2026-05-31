from app.rag.state import ChatState
from app.rag.memory_store import session_memory

def memory_node(state: ChatState) -> ChatState:
    session_id = state.get("session_id", "default")
    
    history = session_memory.get(session_id, [])
    
    state["history"] = history
    return state
