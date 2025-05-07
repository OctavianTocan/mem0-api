from fastapi import FastAPI
from pydantic import BaseModel
from mem0 import Memory
from typing import List, Dict, Any
import os
import json
import openai
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Memory categories
MEMORY_CATEGORIES = [
    "general",
    "personal",
    "work",
    "education",
    "health",
    "finance",
    "ideas",
    "projects",
    "meetings",
    "important"
]

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
        "model": "gpt-4.1-nano"
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

def get_categories(content: str) -> List[str]:
    """
    Use OpenAI to categorize the memory content based on predefined categories.
    Returns a list of relevant categories.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": f"""
                You are a helpful assistant that categorizes memories. 
                For the given memory content, return a JSON array of 1-3 most relevant categories.
                Only use these categories: {', '.join(MEMORY_CATEGORIES)}.
                If no category fits, use ["general"].
                """},
                {"role": "user", "content": content}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        # Parse the response
        categories = json.loads(response.choices[0].message.content)
        if not isinstance(categories, list):
            categories = [categories]
        return categories
    except Exception as e:
        print(f"Error categorizing memory: {e}")
        return ["general"]

@app.post("/add_memory")
def add_memory(chat: ChatInput):
    # Get categories for the memory
    categories = get_categories(chat.message)
    
    # Add the memory with categories in metadata
    memory.add(
        content=chat.message,
        user_id=chat.user_id,
        metadata={"categories": categories},
        infer=False
    )
    return {"status": "memory added", "categories": categories}

@app.delete("/delete_memory")
def delete_memory(chat: ChatInput):
    memory.delete(chat.message, user_id=chat.user_id)
    return {"status": "memory deleted"}

@app.get("/get_memory_categories", response_model=List[str])
def get_memory_categories():
    """
    Get a list of all possible categories that can be assigned to a memory.
    """
    return MEMORY_CATEGORIES

@app.get("/get_all_memories")
def get_all_memories(user_id: str = DEFAULT_USER_ID):
    return memory.get_all(user_id=user_id)
