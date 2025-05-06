#testing @app.post("/add_memory")
import requests
response = requests.post("https://databases.memory.octaviantocan.com/add_memory", json={"message": "Hello, world!", "user_id": "default_user_id"})
print(response.json())

# testing https://databases.memory.octaviantocan.com/get_all_memories
import requests
response = requests.get("https://databases.memory.octaviantocan.com/get_all_memories")
print(response.json())