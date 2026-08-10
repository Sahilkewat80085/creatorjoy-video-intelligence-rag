import sys
import os
import logging
from typing import Optional, List, Dict, Any

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag.nodes.prompt_node import prompt_node
from app.rag.nodes.generator_node import generator_node

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def run_test(test_name: str, question: str, expected_phrase: Optional[str] = None) -> None:
    logger.info("Running test: %s", test_name)
    logger.info("Question: %s", question)
    
    initial_state = {
        "session_id": f"test_session_{test_name.replace(' ', '')}",
        "question": question,
        "history": [],
        "retrieved_chunks": [],
        "citations": [],
        "answer": ""
    }
    
    try:
        # Run only prompt and generator nodes
        state = prompt_node(initial_state)
        result = generator_node(state)
        answer = result.get("answer", "")
    except Exception as e:
        logger.exception("Node execution crashed during test: %s", test_name)
        raise e
    
    logger.info("Generated Answer: %s", answer)
    
    if expected_phrase:
        assert expected_phrase in answer, f"Expected phrase '{expected_phrase}' was not found in answer."
        logger.info("PASS: Answer contains expected phrase: '%s'", expected_phrase)


def run_all_tests() -> None:
    # Test A: Unrelated question
    run_test(
        "Test A (Unrelated Question)", 
        "What is the capital of France?", 
        "I cannot determine this from the available video data."
    )
    
    mock_context_b_c = [{
        "text": "Video B metadata - Creator: Shubhangi Jaiswal, Engagement Rate: 5.92%. Transcript: We went to the mall today.",
        "video_id": "DX4XJj9N8QH"
    }]
    
    logger.info("Running Test B (Creator identification check)...")
    question_b = "Who is the creator of Video B?"
    state_b = {
        "session_id": "test_b",
        "question": question_b,
        "history": [], 
        "retrieved_chunks": mock_context_b_c,
        "citations": [],
        "answer": ""
    }
    
    try:
        state_b = prompt_node(state_b)
        result_b = generator_node(state_b)
        answer_b = result_b.get('answer', '')
    except Exception as e:
        logger.exception("Failed to run Test B nodes.")
        raise e
        
    logger.info("Answer: %s", answer_b)
    assert "Shubhangi" in answer_b, "Answer did not identify creator ('Shubhangi')."
    logger.info("PASS: Answer correctly identifies creator.")

    logger.info("Running Test C (Engagement rate verification)...")
    question_c = "What is the engagement rate of Video B?"
    state_c = {
        "session_id": "test_c",
        "question": question_c,
        "history": [], 
        "retrieved_chunks": mock_context_b_c,
        "citations": [],
        "answer": ""
    }
    
    try:
        state_c = prompt_node(state_c)
        result_c = generator_node(state_c)
        answer_c = result_c.get('answer', '')
    except Exception as e:
        logger.exception("Failed to run Test C nodes.")
        raise e
        
    logger.info("Answer: %s", answer_c)
    assert "5.92" in answer_c, "Answer did not identify engagement rate ('5.92%')."
    logger.info("PASS: Answer correctly identifies engagement rate.")


if __name__ == "__main__":
    try:
        run_all_tests()
        logger.info("All citation grounding tests completed successfully!")
        sys.exit(0)
    except AssertionError as ae:
        logger.error("Grounding assertion check failed: %s", ae)
        sys.exit(1)
    except Exception as e:
        logger.exception("Grounding verification test suite failed with error.")
        sys.exit(1)

