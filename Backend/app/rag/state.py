from typing import TypedDict, List, Dict
from typing_extensions import NotRequired

class ChatState(TypedDict):
    session_id: str
    question: str
    history: NotRequired[List[Dict]]
    retrieved_chunks: NotRequired[List[Dict]]
    citations: NotRequired[List[Dict]]
    prompt: NotRequired[str]
    answer: NotRequired[str]
