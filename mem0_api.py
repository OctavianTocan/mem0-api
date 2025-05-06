from fastapi import FastAPI
from pydantic import BaseModel
from mem0 import Memory
import os
from dotenv import load_dotenv
load_dotenv()

# DEFAULT_USER_ID
DEFAULT_USER_ID = "default_user_id"

app = FastAPI()
PERSIST_DIR = "./memories"
os.makedirs(PERSIST_DIR, exist_ok=True)

memory = Memory.from_config({
    "vector_store": {
        "provider": "chroma",
        "config": { "path": PERSIST_DIR }
    },
    "version": "v2",
    "llm": {
        "provider": "openai",
        "config": {}
    }
})

class ChatInput(BaseModel):
    message: str
    user_id: str = DEFAULT_USER_ID

@app.post("/get_memory")
def get_memory(chat: ChatInput, limit: int = 1):
    return memory.search(
        query=chat.message,
        user_id=chat.user_id,
        limit=limit
    )

@app.post("/add_memory")
def add_memory(chat: ChatInput):
    memory.add(chat.message, user_id=chat.user_id, infer=False)
    return {"status": "memory added"}

@app.delete("/delete_memory")
def delete_memory(chat: ChatInput):
    memory.delete(chat.message, user_id=chat.user_id)
    return {"status": "memory deleted"}

@app.get("/get_all_memories")
def get_all_memories(user_id: str = DEFAULT_USER_ID):
    return memory.get_all(user_id=user_id)
