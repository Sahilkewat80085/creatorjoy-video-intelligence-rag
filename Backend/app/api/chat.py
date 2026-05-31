from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.graph import app as langgraph_app

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    question: str

@router.post("/api/chat")
def chat(request: ChatRequest):
    initial_state = {
        "session_id": request.session_id,
        "question": request.question,
        "history": [],
        "retrieved_chunks": [],
        "citations": [],
        "answer": ""
    }
    
    result = langgraph_app.invoke(initial_state)
    
    return {"answer": result.get("answer", "")}
