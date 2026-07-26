import os
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from app.rag.state import ChatState
from app.rag.memory_store import session_memory
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)

# Ensure env is loaded
load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        logger.exception("Failed to initialize Gemini model in generator_node.py.")
        model = None
else:
    logger.warning("GEMINI_API_KEY is not set in environment variables. generator_node will return fallback responses.")
    model = None


def generator_node(state: ChatState) -> ChatState:
    """
    LangGraph node that calls Gemini API to generate RAG response based on structured context prompt,
    evaluates and filters citations actually used in the answer, and stores interaction in conversation history.
    
    Args:
        state: The current ChatState containing retrieval chunks and generated prompt.
        
    Returns:
        The updated ChatState containing the generated answer.
    """
    prompt = state.get("prompt", "")
    question = state.get("question", "")
    
    # Initialize defaults
    state["answer"] = "I cannot determine this from the available video data."

    if not prompt:
        logger.warning("Empty prompt passed to generator_node. Returning fallback answer.")
        return state

    if model is None:
        logger.error("Gemini model is not initialized (missing API key or initialization failure). Returning fallback answer.")
        state["answer"] = "I cannot determine this from the available video data due to model configuration issues."
        return state
    
    try:
        logger.info("Calling Gemini API to generate response for prompt...")
        response = model.generate_content(prompt)
        answer = response.text
        state["answer"] = answer
        logger.info("Successfully generated response from Gemini model.")
    except ValueError as ve:
        logger.warning("Gemini model generated empty or block-filtered response: %s", ve)
        state["answer"] = "I cannot determine this from the available video data. The model was unable to generate a valid response."
        answer = state["answer"]
    except Exception as e:
        logger.exception("Gemini API call failed during content generation.")
        state["answer"] = f"An error occurred while generating the response: {str(e)}"
        answer = state["answer"]
    
    # Filter citations
    from app.rag.citation_evaluator import filter_citations
    all_citations = state.get("citations", [])
    if all_citations and question:
        try:
            logger.info("Filtering %d retrieved citations...", len(all_citations))
            filtered = filter_citations(question, answer, all_citations)
            state["citations"] = filtered
        except Exception as ce:
            logger.exception("Error occurred while filtering citations: %s", ce)
            # Retain original citations in case of evaluator failure
    
    # Save to history
    session_id = state.get("session_id", "default")
    try:
        history = session_memory.get(session_id, [])
        if not isinstance(history, list):
            history = []
        
        history.append({
            "role": "user",
            "content": question
        })
        
        history.append({
            "role": "assistant",
            "content": answer
        })
        
        session_memory[session_id] = history
        logger.info("Saved user prompt and response in history for session: %s", session_id)
    except Exception as he:
        logger.error("Failed to update session memory in generator_node: %s", he)
    
    return state

