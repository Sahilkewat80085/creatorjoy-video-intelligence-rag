import sys
import os
import logging
from dotenv import load_dotenv

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Ensure environment variables are loaded
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app.rag.graph import app

logger.info("Initializing LangGraph execution test...")

# Setup proper initial state structure adhering to ChatState schemas
initial_state = {
    "session_id": "test_graph_session",
    "question": "What is this song about?",
    "history": [],
    "retrieved_chunks": [],
    "citations": [],
    "answer": ""
}

try:
    logger.info("Invoking compiled StateGraph pipeline...")
    result = app.invoke(initial_state)
    
    logger.info("Graph execution complete.")
    print("\n--- Final Graph Generated Answer ---")
    print(result.get("answer", "No answer field found in state."))
    print("-------------------------------------\n")
    sys.exit(0)
except Exception as e:
    logger.exception("Failed to execute LangGraph pipeline test.")
    sys.exit(1)

