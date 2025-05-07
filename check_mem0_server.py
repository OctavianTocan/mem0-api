import requests

BASE_URL = "https://databases.memory.octaviantocan.com"
DEFAULT_USER_ID = "default_user_id"


def test_add_memory():
    print("Testing /add_memory ...", end=" ")
    data = {"message": "Hello, world!", "user_id": DEFAULT_USER_ID}
    try:
        r = requests.post(f"{BASE_URL}/add_memory", json=data)
        r.raise_for_status()
        print("OK", r.json())
    except Exception as e:
        print("FAILED", e)

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
