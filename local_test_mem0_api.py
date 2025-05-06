#testing https://databases.memory.octaviantocan.com/get_all_memories
import requests
response = requests.get("https://databases.memory.octaviantocan.com/get_all_memories")
print(response.json())