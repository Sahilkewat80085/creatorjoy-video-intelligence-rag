from typing import TypedDict, List, Dict, Any
from typing_extensions import NotRequired


class ChatState(TypedDict):
    """
    Schema definition for the LangGraph Chat RAG State.
    Maintains variables across different execution graph nodes (Memory, Retriever, Prompt, Generator).
    """

    session_id: str
    """Unique identifier representing the current conversation session (used for message history)."""

    question: str
    """The latest user query/question text."""

    history: NotRequired[List[Dict[str, Any]]]
    """Conversation history containing preceding interactions in the shape: [{'role': 'user'|'assistant', 'content': str}]."""

    retrieved_chunks: NotRequired[List[Dict[str, Any]]]
    """List of retrieved text chunks matching the query embeddings, loaded from the vector database payload."""

    citations: NotRequired[List[Dict[str, Any]]]
    """List of source metadata and transcript citations verified to support the generated response."""

    prompt: NotRequired[str]
    """The final structured prompt string constructed by the prompt node, ready to be sent to the LLM."""

    answer: NotRequired[str]
    """The generative response text returned by the LLM (or fallback message if generation failed)."""

