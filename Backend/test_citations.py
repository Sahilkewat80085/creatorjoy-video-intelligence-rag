import sys
import os
import logging

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag.nodes.prompt_node import prompt_node
from app.rag.nodes.generator_node import generator_node
from app.rag.citation_evaluator import filter_citations

# Configure basic logging to stream to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def test_citation(test_name: str, question: str, expected_sources: set, mock_chunks: list, mock_citations: list) -> None:
    logger.info("Starting test: %s", test_name)
    logger.info("Question: %s", question)
    
    state = {
        "session_id": f"test_{test_name.replace(' ', '')}",
        "question": question,
        "history": [],
        "retrieved_chunks": mock_chunks,
        "citations": mock_citations,
        "answer": ""
    }
    
    try:
        state = prompt_node(state)
        state = generator_node(state)
    except Exception as e:
        logger.exception("Failed to execute nodes during test: %s", test_name)
        raise e
    
    citations = state.get("citations", [])
    logger.info("Answer: %s", state.get('answer', ''))
    logger.info("Citations Returned count: %d", len(citations))
    
    sources = set([c.get("source") for c in citations if c.get("source")])
    logger.info("Sources returned: %s", sources)
    
    if expected_sources == set():
        assert len(citations) == 0, f"Expected Empty citations, got: {sources}"
        logger.info("PASS: %s - Citation sources match expected (Empty).", test_name)
    else:
        assert sources == expected_sources, f"Expected {expected_sources}, got: {sources}"
        logger.info("PASS: %s - Citation sources match expected.", test_name)


if __name__ == "__main__":
    mock_chunks = [{
        "text": "Video A metadata - Creator: John Doe, Views: 1000, Likes: 50, Comments: 10, Engagement Rate: 6.0%. Transcript: In this video, we are talking about machine learning and its applications.",
        "video_id": "vidA123",
        "label": "Video A",
        "chunk_index": 0
    }, {
        "text": "Video B metadata - Creator: Jane Smith, Views: 5000, Likes: 500, Comments: 50, Engagement Rate: 11.0%. Transcript: We went to the mall today. It was very crowded, which explains the high engagement.",
        "video_id": "vidB456",
        "label": "Video B",
        "chunk_index": 0
    }]
    
    mock_citations = [
        {"source": "metadata", "video": "A"},
        {"source": "transcript", "video_id": "vidA123", "chunk_index": 0, "score": 0.95},
        {"source": "metadata", "video": "B"},
        {"source": "transcript", "video_id": "vidB456", "chunk_index": 0, "score": 0.92}
    ]

    try:
        test_citation("Test 1 Metadata (Creator)", "Who is the creator of Video B?", {"metadata"}, mock_chunks, mock_citations)
        test_citation("Test 2 Metadata (Engagement)", "What is the engagement rate of Video B?", {"metadata"}, mock_chunks, mock_citations)
        test_citation("Test 3 Transcript", "What does Video A talk about?", {"transcript"}, mock_chunks, mock_citations)
        test_citation("Test 4 Both", "Why might Video B have higher engagement?", {"metadata", "transcript"}, mock_chunks, mock_citations)
        logger.info("All citation verification tests passed successfully!")
    except AssertionError as ae:
        logger.error("Citation assertion check failed: %s", ae)
        sys.exit(1)
    except Exception as e:
        logger.exception("Citation evaluation test suite failed with error.")
        sys.exit(1)

