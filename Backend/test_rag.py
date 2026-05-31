import sys
import os
from dotenv import load_dotenv, find_dotenv

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(find_dotenv())

from app.rag.rag_pipeline import SimpleRAGPipeline

print("Initializing RAG Pipeline...")
rag = SimpleRAGPipeline()

question = "What is this song about?"
print(f"\nQuestion: {question}")
print("\nThinking (Retrieving and Generating)...")

try:
    answer = rag.ask(question)
    print("\n--- Answer ---")
    print(answer)
except Exception as e:
    print(f"\nError: {e}")
