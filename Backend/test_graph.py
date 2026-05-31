import sys
import os
from dotenv import load_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app.rag.graph import app

print("Testing LangGraph execution...")
initial_state = {
    "question": "What is this song about?"
}

result = app.invoke(initial_state)

print("\n--- Final Graph State ---")
print(result["answer"])
