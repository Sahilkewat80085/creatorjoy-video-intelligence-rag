import os
import google.generativeai as genai
from app.rag.state import ChatState
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
    
    state["answer"] = response.text
    return state
