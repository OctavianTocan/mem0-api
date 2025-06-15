from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from mem0 import Memory
from typing import List, Dict, Any
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# region Logging
# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# endregion Logging

# Initialize OpenAI client
MEMORY_API_KEY = os.getenv("MEMORY_API_KEY")
MEMORY_SEARCH_LIMIT = os.getenv("MEMORY_SEARCH_LIMIT", 100)
DB_COLLECTION_NAME = os.getenv("DB_COLLECTION_NAME", "mem0")

# LLM and Embedder configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "models/gemini-2.5-flash")
LLM_MAX_TOKENS = os.getenv("LLM_MAX_TOKENS", 2000)

# Embedder configuration
EMBEDDER_PROVIDER = os.getenv("EMBEDDER_PROVIDER", "gemini")
EMBEDDER_MODEL = os.getenv("EMBEDDER_MODEL", "models/text-embedding-004")
EMBEDDER_DIMENSIONS = os.getenv("EMBEDDER_DIMENSIONS", 768)

# Database configuration
DATABASE_PROVIDER = os.getenv("DATABASE_PROVIDER", "redis")
REDIS_URL = os.getenv("REDIS_URL", "redis://default:IItjAwTwSRcRqOSRBFPOXgKttpvjNDoL@redis-stack.railway.internal:6379")

# Graph provider configuration
GRAPH_PROVIDER_URL = os.getenv("GRAPH_PROVIDER_URL", "neo4j://69.62.122.245:7687")
GRAPH_PROVIDER_USERNAME = os.getenv("GRAPH_PROVIDER_USERNAME", "Tavi")
GRAPH_PROVIDER_PASSWORD = os.getenv("GRAPH_PROVIDER_PASSWORD", "Password123")

# DEFAULT_USER_ID
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "default-researcher-id")
DEFAULT_AGENT_ID = os.getenv("DEFAULT_AGENT_ID", "default-agent-id")

app = FastAPI()

# API key verification. If the API key is not valid, raise a 401 Unauthorized error.
def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> None:
    if x_api_key != MEMORY_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# region Memory Configuration
memory_config = {
    "vector_store": {
        "provider": DATABASE_PROVIDER,
        "config": {
            "collection_name": DB_COLLECTION_NAME,
            "embedding_model_dims": EMBEDDER_DIMENSIONS,
            "redis_url": REDIS_URL
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": GRAPH_PROVIDER_URL,
            "username": GRAPH_PROVIDER_USERNAME,
            "password": GRAPH_PROVIDER_PASSWORD
        }
    },
    "version": "v2",
    "llm": {
        "provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "max_tokens": LLM_MAX_TOKENS
    },
    "embedder": {
        "provider": EMBEDDER_PROVIDER,
        "config": {
            "model": EMBEDDER_MODEL
        }
    }
}
# endregion Memory Configuration

# Initialize memory
memory = Memory.from_config(memory_config)

class SearchInput(BaseModel):
    query: str
    user_id: str = DEFAULT_USER_ID
    agent_id: str = DEFAULT_AGENT_ID

"""
[
  {
    "role": "user",
    "content": {{$('Actual User Message').item.json.chatInput.toJsonString()}}
  },
  {
    "role": "assistant",
    "content": {{$('AI Agent').item.json.output.toJsonString()}}
  }
]
"""
class AddMemoryInput(BaseModel):
    messages: List[Dict[str, str]]
    user_id: str = DEFAULT_USER_ID
    agent_id: str = DEFAULT_AGENT_ID
    infer: bool = True
    metadata: Dict[str, Any] = {}
    
# Super simple ping endpoint.
@app.post("/ping")
def ping():
    return "pong", 200
    

@app.post("/search_memory")
def search_memory(
    search: SearchInput,
    x_api_key: str = Depends(verify_api_key)
) -> dict[str, Any]:
    """
    Search for memories based on the query.
    """
    try:
        logger.info(f"Searching for memories using query: {search.query}")
        logger.info(f"User ID: {search.user_id}, Agent ID: {search.agent_id}")
        
        result = memory.search(
            query=search.query,
            user_id=search.user_id,
            agent_id=search.agent_id,
            limit=MEMORY_SEARCH_LIMIT
        )
        
        logger.info(f"Found {len(result.get('results', []))} memories")
        logger.info(f"Search results: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in search_memory: {str(e)}")
        return {"status": "error", "message": str(e), "results": []}

@app.post("/add_memory")
def add_memory(
    add_memory: AddMemoryInput,
    x_api_key: str = Depends(verify_api_key)
) -> dict[str, Any]:
    try:
        logger.info(f"Adding memories for user: {add_memory.user_id}")
        logger.info(f"Agent ID: {add_memory.agent_id}")
        logger.info(f"Infer mode: {add_memory.infer}")
        logger.info(f"Messages: {add_memory.messages}")
        logger.info(f"Metadata: {add_memory.metadata}")
        

        result = memory.add(
            add_memory.messages, 
            user_id=add_memory.user_id, 
            agent_id=add_memory.agent_id,
            infer=add_memory.infer,
            metadata=add_memory.metadata
        )
        
        logger.info(f"Memories added successfully: {result}")
        
        # Log what memories were actually created
        if 'results' in result:
            for mem in result['results']:
                logger.info(f"Memory created: {mem}")
        
        return {"status": "memory added", "result": result}
    except Exception as e:
        logger.error(f"Error in add_memory: {str(e)}")
        return {"status": "error", "message": str(e)}

def get_all_memories(
    user_id: str = DEFAULT_USER_ID,
    x_api_key: str = Depends(verify_api_key)
) -> dict[str, Any]:
    try:
        logger.info(f"Getting all memories for user: {user_id}")
        result = memory.get_all(user_id=user_id)
        logger.info(f"Found {len(result)} total memories")
        
        return {"status": "success", "memories": result, "count": len(result)}
    except Exception as e:
        logger.error(f"Error in get_all_memories: {str(e)}")
        return {"status": "error", "message": str(e), "memories": []}

@app.post("/delete_all_memories")
def delete_all_memories(
    x_api_key: str = Depends(verify_api_key)
) -> dict[str, str]:
    try:
        logger.info("Deleting all memories")
        memory.reset()
        logger.info("All memories deleted successfully")
        return {"status": "memory deleted"}
    except Exception as e:
        logger.error(f"Error in delete_all_memories: {str(e)}")
        return {"status": "error", "message": str(e)}

# region Debugging
@app.get("/debug_memory_stats")
def debug_memory_stats(
    user_id: str = DEFAULT_USER_ID,
    x_api_key: str = Depends(verify_api_key)
) -> dict[str, Any]:
    """
    Debug endpoint to check memory system status
    """
    try:
        all_memories = memory.get_all(user_id=user_id)
        
        stats = {
            "user_id": user_id,
            "total_memories": len(all_memories),
            "embedding_dimensions": EMBEDDER_DIMENSIONS,
            "llm_model": LLM_MODEL,
            "embedder_model": EMBEDDER_MODEL,
            "memories_preview": all_memories[:5] if all_memories else []
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error in debug_memory_stats: {str(e)}")
        return {"status": "error", "message": str(e)}
# endregion Debugging