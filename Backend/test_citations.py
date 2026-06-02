import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.rag.nodes.prompt_node import prompt_node
from app.rag.nodes.generator_node import generator_node
from app.rag.citation_evaluator import filter_citations

def test_citation(test_name, question, expected_sources, mock_chunks, mock_citations):
    print(f"\n--- {test_name} ---")
    print(f"Question: {question}")
    
    state = {
        "session_id": f"test_{test_name.replace(' ', '')}",
        "question": question,
        "history": [],
        "retrieved_chunks": mock_chunks,
        "citations": mock_citations,
        "answer": ""
    }
    
    state = prompt_node(state)
    state = generator_node(state) # This will automatically call filter_citations because we updated it
    
    citations = state.get("citations", [])
    print(f"Answer: {state.get('answer', '')}")
    print(f"Citations Returned: {len(citations)}")
    
    sources = set([c.get("source") for c in citations])
    print(f"Sources: {sources}")
    
    if expected_sources == set():
        if len(citations) == 0:
            print("PASS: Citation sources match expected (Empty).")
        else:
            print(f"FAIL: Expected Empty, got {sources}")
    elif sources == expected_sources:
        print("PASS: Citation sources match expected.")
    else:
        print(f"FAIL: Expected {expected_sources}, got {sources}")

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

    test_citation("Test 1 Metadata (Creator)", "Who is the creator of Video B?", {"metadata"}, mock_chunks, mock_citations)
    test_citation("Test 2 Metadata (Engagement)", "What is the engagement rate of Video B?", {"metadata"}, mock_chunks, mock_citations)
    test_citation("Test 3 Transcript", "What does Video A talk about?", {"transcript"}, mock_chunks, mock_citations)
    test_citation("Test 4 Both", "Why might Video B have higher engagement?", {"metadata", "transcript"}, mock_chunks, mock_citations)
