from fastapi import FastAPI
from pydantic import BaseModel
from mem0 import Memory
import os

app = FastAPI()

# Use persistent Chroma in Railway’s persistent volume (later)
PERSIST_DIR = "./memories"
os.makedirs(PERSIST_DIR, exist_ok=True)

memory = Memory.from_config({
    "vector_store": {
        "provider": "chroma",
        "config": {
            "persist_directory": PERSIST_DIR
        }
    },
    "version": "v1.1"
})


# Chat input model
class ChatInput(BaseModel):
    message: str
    user_id: str = "default_user"

# Get a memory from the database
@app.get("/get_memory")
def get_memory(message: str):
    return memory.search(query=message, user_id="default_user", limit=1)

# Add a memory to the database
@app.post("/add_memory")
def add_memory(message: str):
    memory.add(message, user_id="default_user")

# Delete a memory from the database
@app.delete("/delete_memory")
def delete_memory(message: str):
    memory.delete(message, user_id="default_user")

# Get all memories from the database
@app.get("/get_all_memories")
def get_all_memories():
    return memory.get_all(user_id="default_user")
