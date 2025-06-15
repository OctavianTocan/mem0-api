import requests
import argparse
import os
import json
from dotenv import load_dotenv

BASE_URL = "https://memory.research.octaviantocan.com"

# region Delete Memory
def delete_memory(message, user_id, api_key):
    """Helper function to delete a memory"""
    try:
        r = requests.post(f"{BASE_URL}/delete_memory", 
                        json={"message": message, "user_id": user_id},
                        headers={"X-API-Key": api_key})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Failed to delete memory: {e}")
        return None
#endregion

# region Add Memory
def test_add_memory(user_id, api_key):
    print("Testing /add_memory ...", end=" ")
    test_message = "Hello, world!"
    data = {"message": test_message, "user_id": user_id}
    try:
        # Add memory
        r = requests.post(f"{BASE_URL}/add_memory", json=data, headers={"X-API-Key": api_key})
        r.raise_for_status()
        add_result = r.json()
        print("OK", add_result)
        
        # Clean up by deleting the memory
        delete_result = delete_memory(test_message, user_id, api_key)
        if delete_result and delete_result.get("success"):
            print("  Cleanup: Memory deleted successfully")
        else:
            print("  Warning: Failed to clean up test memory")
            
    except Exception as e:
        print("FAILED", e)
        # Try to clean up even if the test failed
        delete_memory(test_message, user_id, api_key)
#endregion
# region Get Memory
def test_get_memory(user_id, api_key):
    print("Testing /get_memory ...", end=" ")
    data = {"message": "Hello", "user_id": user_id}
    try:
        r = requests.post(f"{BASE_URL}/get_memory", json=data, headers={"X-API-Key": api_key})
        r.raise_for_status()
        print("OK", r.json())
    except Exception as e:
        print("FAILED", e)
#endregion

# region Save Memories Locally
def save_memories_locally(memories):
    os.makedirs("memories", exist_ok=True)
    path = os.path.join("memories", "all_memories.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(memories.get('results', []))} memories to {path}")
#endregion

# region Get All Memories
def test_get_all_memories(user_id, api_key):
    print("Testing /get_all_memories ...", end=" ")
    try:
        r = requests.get(f"{BASE_URL}/get_all_memories", params={"user_id": user_id}, headers={"X-API-Key": api_key})
        r.raise_for_status()
        data = r.json()
        print("OK", f"{len(data.get('results', []))} memories")
        save_memories_locally(data)
    except Exception as e:
        print("FAILED", e)
#endregion

# region Reset Memories
def delete_all_memories(user_id, api_key):
    """Reset the memory server."""
    try:
        requests.post(f"{BASE_URL}/delete_all_memories", params={"user_id": user_id}, headers={"X-API-Key": api_key})
    except Exception as e:
        print("FAILED", e)
#endregion

# region Search Memories
def search_memories(query, user_id, api_key):
    print(f"Searching for '{query}' in memories ...", end=" ")
    try:
        r = requests.get(f"{BASE_URL}/get_all_memories", params={"user_id": user_id}, headers={"X-API-Key": api_key})
        r.raise_for_status()
        data = r.json()
        memories = data.get("results", [])
        matches = [mem for mem in memories if query.lower() in mem.get("message", "").lower()]
        print(f"Found {len(matches)} matches:")
        for mem in matches:
            print("-", mem.get("message"))
    except Exception as e:
        print("FAILED", e)
#endregion

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test mem0 server endpoints.")
    parser.add_argument("command", choices=["reset", "save", "search", "add", "getall"], help="Action to perform")
    parser.add_argument("--query", type=str, help="Query string for search")
    parser.add_argument("--user", type=str, required=False, help="User ID to operate on")
    parser.add_argument("--api-key", type=str, required=False, help="API key for authentication (or set MEMORY_API_KEY in .env)")
    args = parser.parse_args()

    user_id = args.user
    api_key = args.api_key
    if not api_key:
        load_dotenv()
        api_key = os.getenv("MEMORY_API_KEY")
    if not api_key:
        print("Error: API key not provided. Use --api-key or set MEMORY_API_KEY in .env.")
        exit(1)

    if args.command == "reset":
        delete_all_memories(user_id, api_key)
    elif args.command == "save":
        test_get_all_memories(user_id, api_key)
    elif args.command == "search":
        if not args.query:
            print("--query argument required for search")
        else:
            search_memories(args.query, user_id, api_key)
    elif args.command == "add":
        test_add_memory(user_id, api_key)
    elif args.command == "getall":
        test_get_all_memories(user_id, api_key)
