from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.graph import app as langgraph_app

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/api/chat")
def chat(request: ChatRequest):
    initial_state = {
        "question": request.question
    }
    
    result = langgraph_app.invoke(initial_state)
    
    return {"answer": result.get("answer", "")}
