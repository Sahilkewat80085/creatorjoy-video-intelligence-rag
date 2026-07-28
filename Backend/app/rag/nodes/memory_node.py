import logging
from app.rag.state import ChatState
from app.rag.memory_store import session_memory

logger = logging.getLogger(__name__)


def memory_node(state: ChatState) -> ChatState:
    """
    LangGraph node that retrieves historical messages from session memory for the current session.
    
    Args:
        state: The current ChatState.
        
    Returns:
        The updated ChatState containing the loaded history.
    """
    session_id = state.get("session_id", "default")
    
    # Precondition validation: ensure session_id is a non-empty string
    if not isinstance(session_id, str) or not session_id.strip():
        logger.warning("Invalid or empty session_id '%s' passed to memory_node. Falling back to 'default'.", session_id)
        session_id = "default"
        state["session_id"] = session_id
        
    try:
        logger.info("Retrieving conversation history for session_id: %s", session_id)
        history = session_memory.get(session_id, [])
        if not isinstance(history, list):
            logger.warning("History retrieved for session '%s' is not a list. Initializing empty list.", session_id)
            history = []
    except Exception as e:
        logger.exception("Failed to load conversation history from session memory for session: %s", session_id)
        # Graceful degradation: default to empty conversation history rather than crashing the pipeline execution
        history = []
        
    state["history"] = history
    logger.info("Successfully loaded %d messages from history for session: %s", len(history), session_id)
    return state

