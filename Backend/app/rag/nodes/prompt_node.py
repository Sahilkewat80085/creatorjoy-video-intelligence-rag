import logging
from app.rag.state import ChatState

logger = logging.getLogger(__name__)


def prompt_node(state: ChatState) -> ChatState:
    """
    LangGraph node that constructs a structured retrieval-augmented generation (RAG) prompt
    for the Gemini model based on retrieved contexts, history, and the current question.
    
    Args:
        state: The current ChatState.
        
    Returns:
        The updated ChatState with the generated prompt populated.
    """
    logger.info("Constructing generation prompt...")
    
    retrieved_chunks = state.get("retrieved_chunks", [])
    if not isinstance(retrieved_chunks, list):
        logger.warning("retrieved_chunks in ChatState is not a list. Initializing empty list.")
        retrieved_chunks = []
    
    # Process retrieved chunks safely, checking types
    context_parts = []
    for chunk in retrieved_chunks:
        if isinstance(chunk, dict):
            text = chunk.get("text", "")
            if text:
                context_parts.append(text)
        elif hasattr(chunk, "text"):  # Handle potential Pydantic objects or custom classes
            text = getattr(chunk, "text", "")
            if text:
                context_parts.append(str(text))
                
    context = "\n\n".join(context_parts)
    
    # Process history messages safely
    history_text = ""
    history = state.get("history", [])
    if isinstance(history, list):
        for msg in history:
            if isinstance(msg, dict):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"
            else:
                logger.warning("History message is not a dictionary: %s", msg)
    else:
        logger.warning("history in ChatState is not a list: %s", type(history))
    
    question = state.get("question", "")
    if not question:
        logger.warning("Prompt node executed with an empty or missing question in state.")

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
{question}

Answer strictly using both the conversation history and retrieved context."""

    state["prompt"] = prompt
    logger.info("Successfully constructed generation prompt (length: %d chars).", len(prompt))
    return state

