from app.rag.state import ChatState

def prompt_node(state: ChatState) -> ChatState:
    retrieved_chunks = state.get("retrieved_chunks", [])
    
    context = "\n\n".join([chunk.get('text', '') for chunk in retrieved_chunks])
    
    history_text = ""
    for msg in state.get("history", []):
        history_text += f"{msg['role']}: {msg['content']}\n"
    
    prompt = f"""You are a retrieval-augmented assistant.

Use ONLY the provided metadata, conversation history, and retrieved transcript context.

Do NOT use your own world knowledge.

Do NOT infer information that is not explicitly present in the supplied context.

If the answer cannot be determined from the provided context, respond exactly:
'I cannot determine this from the available video data.'

Never guess.
Never hallucinate.
Never use external knowledge.

Previous Conversation:
{history_text}

Retrieved Context:
{context}

Current Question:
{state['question']}

Answer strictly using both the conversation history and retrieved context."""

    state["prompt"] = prompt
    return state
