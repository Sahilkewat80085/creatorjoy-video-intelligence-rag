import json
import os
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

eval_model = genai.GenerativeModel("gemini-1.5-flash")

def filter_citations(question: str, answer: str, all_citations: list) -> list:
    """
    Evaluates the generated answer to determine which citations were actually used.
    """
    if not answer or not all_citations:
        return []

    # Format the citations for the prompt
    citations_json = json.dumps(all_citations, indent=2)
    
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
        # We can use generation config to enforce JSON output
        response = eval_model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        filtered = json.loads(response.text)
        if isinstance(filtered, list):
            return filtered
    except Exception as e:
        print(f"Citation evaluator failed: {e}")
        
    # Fallback to returning all if evaluation fails
    return all_citations
