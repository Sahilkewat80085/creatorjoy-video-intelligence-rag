import sys
import os
import logging
from dotenv import load_dotenv, find_dotenv

# Reconfigure console output encoding to UTF-8 to prevent unicode errors in Windows shells
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Ensure environment variables are loaded
load_dotenv(find_dotenv())

from app.rag.rag_pipeline import SimpleRAGPipeline

logger.info("Initializing RAG Pipeline...")
try:
    rag = SimpleRAGPipeline()
except Exception as e:
    logger.exception("Failed to initialize SimpleRAGPipeline.")
    sys.exit(1)

question = "What is this song about?"
logger.info("Question: %s", question)
logger.info("Thinking (Retrieving and Generating response)...")

try:
    answer = rag.ask(question)
    print("\n--- Generated Answer ---")
    print(answer)
    print("------------------------\n")
except Exception as e:
    logger.error("RAG pipeline execution failed: %s", e)

