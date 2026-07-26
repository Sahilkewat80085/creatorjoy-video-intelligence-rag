import json
import os
import re
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv

# Setup logger for the module
logger = logging.getLogger(__name__)

# Ensure env variables are loaded
load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    logger.warning("GEMINI_API_KEY is not set in the environment variables. Citation evaluator will fallback to original citations.")

# Initialize the model
# We set up the model using the standard GenerativeModel API.
try:
    eval_model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    logger.exception("Failed to initialize Gemini GenerativeModel in citation_evaluator.py.")
    eval_model = None


def clean_json_text(text: str) -> str:
    """
    Cleans markdown code block wraps (like ```json ... ```) from the LLM output.
    """
    text = text.strip()
    # Check if the text is wrapped in markdown code blocks
    if text.startswith("```"):
        match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return text


def filter_citations(question: str, answer: str, citations: List[dict]) -> List[dict]:
    """
    Evaluates the generated answer to determine which citations were actually used.
    
    Args:
        question: The user's query.
        answer: The RAG-generated response.
        citations: List of source citations retrieved.
        
    Returns:
        A list of citation dictionaries verified to be used in the response.
    """
    if not answer or not citations:
        return []

    if not gemini_api_key or eval_model is None:
        logger.warning("Gemini API is not configured. Returning all retrieved citations as fallback.")
        return citations

    # Format the citations for the prompt
    citations_json = json.dumps(citations, indent=2)
    
    prompt = f"""You are a strict citation evaluator.
Your job is to determine which of the provided citations were ACTUALLY used to generate the answer to the user's question.

Question: {question}
Answer: {answer}

Available Citations:
{citations_json}

RULES:
1. If the answer states that it cannot determine the information (e.g., 'I cannot determine this from the available video data.'), return an empty list `[]`.
2. If the answer relies entirely on METADATA (e.g., creator name, views, likes, comments, engagement rate, duration), return ONLY the metadata citations for the relevant videos.
3. If the answer relies on TRANSCRIPT content (what was spoken in the video), return the transcript citations for the relevant videos.
4. If the answer relies on BOTH metadata and transcript, return both.
5. Output MUST be a valid JSON list containing ONLY the subset of citation objects from the Available Citations that were used. Do not modify the citation objects themselves. Do NOT wrap the JSON in markdown code blocks.

Return the JSON array now:"""

    try:
        # We use generation config to enforce JSON output
        response = eval_model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        cleaned_text = clean_json_text(response.text)
        filtered = json.loads(cleaned_text)
        if isinstance(filtered, list):
            logger.info("Successfully filtered citations. Original count: %d, Filtered count: %d", len(citations), len(filtered))
            return filtered
        else:
            logger.warning("Gemini model returned JSON but it was not a list: %s", response.text)
    except Exception as e:
        logger.exception("Citation evaluator failed during API request or JSON parsing.")
        
    # Fallback to returning all if evaluation fails
    return citations

