from app.rag.state import ChatState

def prompt_node(state: ChatState) -> ChatState:
    retrieved_chunks = state.get("retrieved_chunks", [])
    
    context = "\n\n".join([chunk.get('text', '') for chunk in retrieved_chunks])
    
    prompt = f"""You are a creator intelligence assistant.

Context:
{context}

Question:
{state['question']}

Answer using only the provided context."""

    state["prompt"] = prompt
    return state
