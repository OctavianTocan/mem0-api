import requests

BASE_URL = "https://databases.memory.octaviantocan.com"
DEFAULT_USER_ID = "default_user_id"


def delete_memory(message, user_id):
    """Helper function to delete a memory"""
    try:
        r = requests.post(f"{BASE_URL}/delete_memory", 
                        json={"message": message, "user_id": user_id})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Failed to delete memory: {e}")
        return None

def test_add_memory():
    print("Testing /add_memory ...", end=" ")
    test_message = "Hello, world!"
    data = {"message": test_message, "user_id": DEFAULT_USER_ID}
    try:
        # Add memory
        r = requests.post(f"{BASE_URL}/add_memory", json=data)
        r.raise_for_status()
        add_result = r.json()
        print("OK", add_result)
        
        # Clean up by deleting the memory
        delete_result = delete_memory(test_message, DEFAULT_USER_ID)
        if delete_result and delete_result.get("success"):
            print("  Cleanup: Memory deleted successfully")
        else:
            print("  Warning: Failed to clean up test memory")
            
    except Exception as e:
        print("FAILED", e)
        # Try to clean up even if the test failed
        delete_memory(test_message, DEFAULT_USER_ID)

def test_get_memory():
    print("Testing /get_memory ...", end=" ")
    data = {"message": "Hello", "user_id": DEFAULT_USER_ID}
    try:
        r = requests.post(f"{BASE_URL}/get_memory", json=data)
        r.raise_for_status()
        print("OK", r.json())
    except Exception as e:
        print("FAILED", e)

import os
import json

def save_memories_locally(memories):
    os.makedirs("memories", exist_ok=True)
    path = os.path.join("memories", "all_memories.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(memories.get('results', []))} memories to {path}")

def test_get_all_memories():
    print("Testing /get_all_memories ...", end=" ")
    try:
        r = requests.get(f"{BASE_URL}/get_all_memories", params={"user_id": DEFAULT_USER_ID})
        r.raise_for_status()
        data = r.json()
        print("OK", f"{len(data.get('results', []))} memories")
        save_memories_locally(data)
    except Exception as e:
        print("FAILED", e)

if __name__ == "__main__":
    test_add_memory()
    test_get_all_memories()
