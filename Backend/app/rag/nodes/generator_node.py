import os
import google.generativeai as genai
from app.rag.state import ChatState
from app.rag.memory_store import session_memory
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# We use the updated model name directly
model = genai.GenerativeModel("gemini-2.5-flash")

def generator_node(state: ChatState) -> ChatState:
    prompt = state.get("prompt", "")
    
    response = model.generate_content(prompt)
    answer = response.text
    
    state["answer"] = answer
    
    # Filter citations
    from app.rag.citation_evaluator import filter_citations
    all_citations = state.get("citations", [])
    if all_citations:
        filtered = filter_citations(state["question"], answer, all_citations)
        state["citations"] = filtered
    
    session_id = state.get("session_id", "default")
    history = session_memory.get(session_id, [])
    
    history.append({
        "role": "user",
        "content": state["question"]
    })
    
    history.append({
        "role": "assistant",
        "content": answer
    })
    
    session_memory[session_id] = history
    
    return state
