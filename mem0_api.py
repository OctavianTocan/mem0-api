from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from mem0 import Memory
from typing import List, Dict, Any, Optional
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
MEMORY_SEARCH_LIMIT = int(os.getenv("MEMORY_SEARCH_LIMIT", 100))
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
REDIS_URL = os.getenv("REDIS_URL")

# Graph provider configuration
GRAPH_PROVIDER_URL = os.getenv("GRAPH_PROVIDER_URL", )
GRAPH_PROVIDER_USERNAME = os.getenv("GRAPH_PROVIDER_USERNAME")
GRAPH_PROVIDER_PASSWORD = os.getenv("GRAPH_PROVIDER_PASSWORD")

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
    "version": "v2",
    "llm": {
        "provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "max_tokens": LLM_MAX_TOKENS
    },
    "embedder": {
        "provider": EMBEDDER_PROVIDER,
        "config": {
            "model": EMBEDDER_MODEL,
            "embedding_dims": EMBEDDER_DIMENSIONS
        }
    }
}

# Add graph configuration only if GRAPH_PROVIDER_URL is set
if GRAPH_PROVIDER_URL and GRAPH_PROVIDER_USERNAME and GRAPH_PROVIDER_PASSWORD:
    memory_config["graph_store"] = {
        "provider": "neo4j",
        "config": {
            "url": GRAPH_PROVIDER_URL,
            "username": GRAPH_PROVIDER_USERNAME,
            "password": GRAPH_PROVIDER_PASSWORD
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
    prompt: Optional[str] = None

# Move TranscriptHandler import here to avoid circular imports
from memory_utils import TranscriptHandler

# Super simple ping endpoint.
@app.post("/ping")
def ping():
    return "pong", 200


@app.post("/search_memory")
def search_memory(
    search: SearchInput, x_api_key: str = Depends(verify_api_key)
) -> dict[str, Any]:
    """
    Search for memories based on the query.
    """
    try:
        logger.info(f"Searching for memories using query: {search.query}")
        logger.info(f"User ID: {search.user_id}, Agent ID: {search.agent_id}")

        result = memory.search(query=search.query,
                               user_id=search.user_id,
                               agent_id=search.agent_id,
                               limit=MEMORY_SEARCH_LIMIT)

        logger.info(f"Found {len(result.get('results', []))} memories")
        logger.info(f"Search results: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in search_memory: {str(e)}")
        return {"status": "error", "message": str(e), "results": []}


def _add_memory_core(input: AddMemoryInput) -> dict:
    """Core memory adding logic"""
    try:
        logger.info(f"Adding memories for user: {input.user_id}")
        logger.info(f"Agent ID: {input.agent_id}")
        logger.info(f"Infer mode: {input.infer}")
        logger.info(f"Messages: {input.messages}")
        logger.info(f"Metadata: {input.metadata}")
        logger.info(f"Prompt: {input.prompt}")

        result = memory.add(input.messages,
                          user_id=input.user_id,
                          agent_id=input.agent_id,
                          infer=input.infer,
                          metadata=input.metadata,
                          prompt=input.prompt)

        logger.info(f"Memories added successfully: {result}")
        if 'results' in result:
            for mem in result['results']:
                logger.info(f"Memory created: {mem}")
        return {"status": "memory added", "result": result}
    except Exception as e:
        logger.error(f"Error in _add_memory_core: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/add_memory")
def add_memory(
    input: AddMemoryInput, x_api_key: str = Depends(verify_api_key)
) -> dict[str, Any]:
    """Endpoint wrapper for _add_memory_core"""
    return _add_memory_core(input)

class AddTranscriptInput(BaseModel):
    transcript: List[Dict[str, str]]
    user_id: str = DEFAULT_USER_ID
    agent_id: str = DEFAULT_AGENT_ID
    metadata: Dict[str, Any] = {}
    extract_memories: bool = True
    prompt: Optional[str] = None

@app.post("/add_transcript")
def add_transcript(
    input: AddTranscriptInput, 
    x_api_key: str = Depends(verify_api_key)
) -> dict:
    """Add meeting transcript and optionally extract memories"""
    handler = TranscriptHandler()
    # Store raw transcript
    result = handler.store_transcript(
        input.transcript,
        input.user_id,
        input.agent_id,
        input.metadata
    )
    
    # Optionally extract memories
    if input.extract_memories:
        mem_result = handler.extract_memories(
            input.transcript,
            input.user_id,
            input.agent_id,
            input.metadata,
            input.prompt
        )
        result['extracted_memories'] = mem_result
    
    return result


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
def delete_all_memories(x_api_key: str = Depends(verify_api_key)) -> dict[str,
                                                                          str]:
    try:
        logger.info("Deleting all memories")
        memory.reset()
        logger.info("All memories deleted successfully")
        return {"status": "memory deleted"}
    except Exception as e:
        logger.error(f"Error in delete_all_memories: {str(e)}")
        return {"status": "error", "message": str(e)}
