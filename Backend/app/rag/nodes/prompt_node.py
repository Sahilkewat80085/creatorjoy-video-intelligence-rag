from app.rag.state import ChatState

def prompt_node(state: ChatState) -> ChatState:
    retrieved_chunks = state.get("retrieved_chunks", [])
    
    context = "\n\n".join([chunk.get('text', '') for chunk in retrieved_chunks])
    
    history_text = ""
    for msg in state.get("history", []):
        history_text += f"{msg['role']}: {msg['content']}\n"
    
    prompt = f"""You are a creator intelligence assistant.

Previous Conversation:
{history_text}

Retrieved Context:
{context}

Current Question:
{state['question']}

Answer using both the conversation history and retrieved context."""

    state["prompt"] = prompt
    return state
