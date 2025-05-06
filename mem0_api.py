from fastapi import FastAPI
from pydantic import BaseModel
from mem0 import Memory
import os

app = FastAPI()
PERSIST_DIR = "./memories"
os.makedirs(PERSIST_DIR, exist_ok=True)

memory = Memory.from_config({
    "vector_store": {
        "provider": "chroma",
        "config": { "path": PERSIST_DIR }
    },
    "version": "v2"
})

class ChatInput(BaseModel):
    message: str
    user_id: str = "default_user"

@app.post("/get_memory")
def get_memory(chat: ChatInput):
    return memory.search(
        query=chat.message,
        user_id=chat.user_id,
        limit=1,
        version="v2"
    )

@app.post("/add_memory")
def add_memory(chat: ChatInput):
    memory.add(chat.message, user_id=chat.user_id, version="v2")
    return {"status": "memory added"}

@app.delete("/delete_memory")
def delete_memory(chat: ChatInput):
    memory.delete(chat.message, user_id=chat.user_id, version="v2")
    return {"status": "memory deleted"}

@app.get("/get_all_memories")
def get_all_memories(user_id: str = "default_user"):
    return memory.get_all(user_id=user_id, version="v2")
