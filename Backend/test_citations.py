import requests
import json

base_url = "http://localhost:8080/api/chat"

print("--- Test 1: Metadata Citation ---")
payload1 = {
    "session_id": "test-citations-1",
    "question": "Who is the creator of Video B?"
}

response1 = requests.post(base_url, json=payload1)
print(json.dumps(response1.json(), indent=2))

print("\n--- Test 2: Transcript Citation ---")
payload2 = {
    "session_id": "test-citations-2",
    "question": "What is Video A about?"
}

response2 = requests.post(base_url, json=payload2)
print(json.dumps(response2.json(), indent=2))
