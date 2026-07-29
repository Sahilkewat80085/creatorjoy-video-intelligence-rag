import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# session_memory holds the conversation history mapping session ID strings to lists of message dictionaries.
# Each message is represented in the shape: {"role": "user"|"assistant", "content": str}
session_memory: Dict[str, List[Dict[str, Any]]] = {}

