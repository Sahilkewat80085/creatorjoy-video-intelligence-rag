import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag.nodes.prompt_node import prompt_node
from app.rag.nodes.generator_node import generator_node

def run_test(test_name, question, expected_phrase=None):
    print(f"\n--- Running {test_name} ---")
    print(f"Question: {question}")
    
    initial_state = {
        "session_id": f"test_session_{test_name}",
        "question": question,
        "history": [],
        "retrieved_chunks": [],
        "citations": [],
        "answer": ""
    }
    
    # Run only prompt and generator
    state = prompt_node(initial_state)
    result = generator_node(state)
    answer = result.get("answer", "")
    
    print(f"Answer: {answer}")
    
    if expected_phrase:
        if expected_phrase in answer:
            print(f"PASS: Answer contains expected phrase: '{expected_phrase}'")
        else:
            print(f"FAIL: Answer does NOT contain expected phrase: '{expected_phrase}'")
            
def run_all_tests():
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
    
    print(f"\n--- Running Test B ---")
    question_b = "Who is the creator of Video B?"
    print(f"Question: {question_b}")
    
    state_b = {
        "session_id": "test_b", "question": question_b, "history": [], 
        "retrieved_chunks": mock_context_b_c, "citations": [], "answer": ""
    }
    state_b = prompt_node(state_b)
    result_b = generator_node(state_b)
    
    print(f"Answer: {result_b.get('answer', '')}")
    if "Shubhangi" in result_b.get('answer', ''):
        print("PASS: Answer correctly identifies creator.")
    else:
        print("FAIL: Answer did not identify creator.")

    print(f"\n--- Running Test C ---")
    question_c = "What is the engagement rate of Video B?"
    print(f"Question: {question_c}")
    
    state_c = {
        "session_id": "test_c", "question": question_c, "history": [], 
        "retrieved_chunks": mock_context_b_c, "citations": [], "answer": ""
    }
    state_c = prompt_node(state_c)
    result_c = generator_node(state_c)

    print(f"Answer: {result_c.get('answer', '')}")
    if "5.92" in result_c.get('answer', ''):
        print("PASS: Answer correctly identifies engagement rate.")
    else:
        print("FAIL: Answer did not identify engagement rate.")

if __name__ == "__main__":
    run_all_tests()
