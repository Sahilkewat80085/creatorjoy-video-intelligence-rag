from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.rag.graph import app as langgraph_app, stream_app
from app.rag.nodes.generator_node import model
from app.rag.memory_store import session_memory

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
    
    return {
        "answer": result.get("answer", ""),
        "citations": result.get("citations", [])
    }

@router.post("/api/chat/stream")
def stream_chat(request: ChatRequest):
    initial_state = {
        "session_id": request.session_id,
        "question": request.question,
        "history": [],
        "retrieved_chunks": [],
        "citations": [],
        "answer": ""
    }
    
    # Run graph up to prompt node
    result = stream_app.invoke(initial_state)
    prompt = result.get("prompt", "")
    
    def generate():
        import json
        from app.rag.citation_evaluator import filter_citations
        
        response = model.generate_content(prompt, stream=True)
        full_answer = ""
        for chunk in response:
            if chunk.text:
                full_answer += chunk.text
                yield json.dumps({"type": "token", "content": chunk.text}) + "\n"
                
        # Evaluate citations
        all_citations = result.get("citations", [])
        filtered_citations = []
        if all_citations:
            filtered_citations = filter_citations(request.question, full_answer, all_citations)
            
        yield json.dumps({"type": "citations", "citations": filtered_citations}) + "\n"
                
        # Update memory after stream completes
        session_id = request.session_id
        history = session_memory.get(session_id, [])
        history.append({
            "role": "user",
            "content": request.question
        })
        history.append({
            "role": "assistant",
            "content": full_answer
        })
        session_memory[session_id] = history

    return StreamingResponse(generate(), media_type="application/x-ndjson")
