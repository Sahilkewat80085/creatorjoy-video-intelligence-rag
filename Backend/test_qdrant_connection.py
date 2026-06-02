import os
from dotenv import load_dotenv, find_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

def mask_key(key):
    if not key:
        return "None"
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]

def test_qdrant_connection():
    load_dotenv(find_dotenv())
    
    raw_url = os.getenv("QDRANT_URL", "")
    raw_key = os.getenv("QDRANT_API_KEY", "")
    
    print("=== Qdrant Cloud Connection Test ===")
    
    print("\n--- Raw Environment Variables ---")
    print(f"QDRANT_URL repr: {repr(raw_url)}")
    print(f"QDRANT_API_KEY repr: {repr(raw_key)}")
    print(f"QDRANT_API_KEY length: {len(raw_key)}")
    print(f"QDRANT_API_KEY masked: {mask_key(raw_key)}")
    
    qdrant_url = raw_url.strip()
    qdrant_api_key = raw_key.strip()
    
    print("\n--- Sanitized Variables ---")
    print(f"Sanitized URL repr: {repr(qdrant_url)}")
    print(f"Sanitized API Key repr: {repr(qdrant_api_key)}")
    print(f"Sanitized API Key length: {len(qdrant_api_key)}")
    
    if not qdrant_url or not qdrant_api_key:
        print("\n[ERROR] Missing URL or API Key!")
        return

    print("\n--- Testing Connection ---")
    try:
        client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )
        collections = client.get_collections()
        print("[QDRANT] Connection successful")
        print(f"Available collections: {[c.name for c in collections.collections]}")
        
    except Exception as e:
        print("[QDRANT] Connection failed")
        print(f"Exception details: {str(e)}")
        import traceback
        traceback.print_exc()
        return

    print("\n--- Testing Read/Write Operations ---")
    test_collection = "connection_test"
    
    try:
        # Re-create collection to ensure clean state
        try:
            client.delete_collection(test_collection)
        except Exception:
            pass
            
        print(f"Creating collection '{test_collection}'...")
        client.create_collection(
            collection_name=test_collection,
            vectors_config=VectorParams(size=4, distance=Distance.COSINE)
        )
        
        print("Inserting dummy vector...")
        client.upsert(
            collection_name=test_collection,
            points=[
                PointStruct(
                    id=1,
                    vector=[0.1, 0.2, 0.3, 0.4],
                    payload={"test": "data"}
                )
            ]
        )
        
        print("Reading vector back...")
        result = client.retrieve(
            collection_name=test_collection,
            ids=[1]
        )
        if result and len(result) > 0:
            print(f"Successfully retrieved vector payload: {result[0].payload}")
        else:
            print("Failed to retrieve vector.")
            
        print("Deleting collection...")
        client.delete_collection(test_collection)
        
        print("\n=== All Tests Passed Successfully ===")
        
    except Exception as e:
        print("[QDRANT] Operations test failed")
        print(f"Exception details: {str(e)}")

if __name__ == "__main__":
    test_qdrant_connection()
