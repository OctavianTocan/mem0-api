from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from mem0 import Memory
from typing import Any
import os
import logging
from dotenv import load_dotenv
from models import SearchInput, AddMemoryInput, AddTranscriptInput
from transcript_handler import TranscriptHandler

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
GRAPH_PROVIDER_URL = os.getenv(
    "GRAPH_PROVIDER_URL",
)
GRAPH_PROVIDER_USERNAME = os.getenv("GRAPH_PROVIDER_USERNAME")
GRAPH_PROVIDER_PASSWORD = os.getenv("GRAPH_PROVIDER_PASSWORD")

# DEFAULT_USER_ID
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "default-researcher-id")
DEFAULT_AGENT_ID = os.getenv("DEFAULT_AGENT_ID", "default-agent-id")

app = FastAPI(
    title="Mem0 API",
    description="Mem0 API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
)

# region -- CORS Configuration --

# Railway provides these environment variables
railway_static_url = os.getenv("RAILWAY_STATIC_URL")
railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")

allowed_origins = []

# Add custom domains
if os.getenv("CORS_ORIGINS"):
    allowed_origins.extend(os.getenv("CORS_ORIGINS").split(","))

# Add Railway domains
if railway_static_url:
    allowed_origins.append(f"https://{railway_static_url}")
if railway_public_domain:
    allowed_origins.append(f"https://{railway_public_domain}")

# Development origins
if os.getenv("ENVIRONMENT") != "production":
    allowed_origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# endregion -- CORS Configuration --


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
            "redis_url": REDIS_URL,
        },
    },
    "version": "v2",
    "llm": {"provider": LLM_PROVIDER, "model": LLM_MODEL, "max_tokens": LLM_MAX_TOKENS},
    "embedder": {
        "provider": EMBEDDER_PROVIDER,
        "config": {"model": EMBEDDER_MODEL, "embedding_dims": EMBEDDER_DIMENSIONS},
    },
}

# Add graph configuration only if GRAPH_PROVIDER_URL is set
if GRAPH_PROVIDER_URL and GRAPH_PROVIDER_USERNAME and GRAPH_PROVIDER_PASSWORD:
    memory_config["graph_store"] = {
        "provider": "neo4j",
        "config": {
            "url": GRAPH_PROVIDER_URL,
            "username": GRAPH_PROVIDER_USERNAME,
            "password": GRAPH_PROVIDER_PASSWORD,
        },
    }
# endregion Memory Configuration

# Initialize memory
memory = Memory.from_config(memory_config)


@app.get("/")
def read_root():
    return {"status": "ok"}


# Super simple ping endpoint.
@app.post("/ping")
def ping():
    return {"status": "pong"}


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

        result = memory.search(
            query=search.query,
            user_id=search.user_id,
            agent_id=search.agent_id,
            limit=MEMORY_SEARCH_LIMIT,
        )

        logger.info(f"Found {len(result.get('results', []))} memories")
        logger.info(f"Search results: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in search_memory: {str(e)}")
        return {"status": "error", "message": str(e), "results": []}


def _add_memory_core(memory_input: AddMemoryInput) -> dict:
    """Core memory adding logic"""
    try:
        logger.info(f"Adding memories for user: {memory_input.user_id}")
        logger.info(f"Agent ID: {memory_input.agent_id}")
        logger.info(f"Infer mode: {memory_input.infer}")
        logger.info(f"Messages: {memory_input.messages}")
        logger.info(f"Metadata: {memory_input.metadata}")
        logger.info(f"Prompt: {memory_input.prompt}")

        result = memory.add(
            memory_input.messages,
            user_id=memory_input.user_id,
            agent_id=memory_input.agent_id,
            infer=memory_input.infer,
            metadata=memory_input.metadata,
            prompt=memory_input.prompt,
        )

        logger.info(f"Memories added successfully: {result}")
        if "results" in result:
            for mem in result["results"]:
                logger.info(f"Memory created: {mem}")
        return {"status": "memory added", "result": result}
    except Exception as e:
        logger.error(f"Error in _add_memory_core: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/add_memory")
def add_memory(
    memory_input: AddMemoryInput, x_api_key: str = Depends(verify_api_key)
) -> dict[str, Any]:
    """Endpoint wrapper for _add_memory_core"""
    return _add_memory_core(memory_input)


@app.post("/add_transcript")
def add_transcript(
    memory_input: AddTranscriptInput, x_api_key: str = Depends(verify_api_key)
) -> dict[str, Any]:
    """Add meeting transcript and optionally extract memories"""
    try:
        handler = TranscriptHandler()
        result = {"status": "processing"}
        # Store raw transcript
        store_input = handler.store_transcript(
            memory_input.transcript,
            memory_input.user_id,
            memory_input.agent_id,
            memory_input.metadata,
        )
        store_result = _add_memory_core(store_input)

        # Store the transcript in the result
        result["transcript_storage_result"] = store_result

        # Optionally extract memories
        if memory_input.extract_memories:
            extract_input = handler.extract_memories(
                memory_input.transcript,
                memory_input.user_id,
                memory_input.agent_id,
                memory_input.metadata,
                memory_input.prompt,
            )
            extract_result = _add_memory_core(extract_input)
            result["extracted_memories_result"] = extract_result

        return result
    except Exception as e:
        logger.error(f"Error in add_transcript: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/get_all_memories")
def get_all_memories(
    user_id: str = DEFAULT_USER_ID, x_api_key: str = Depends(verify_api_key)
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
def delete_all_memories(x_api_key: str = Depends(verify_api_key)) -> dict[str, str]:
    try:
        logger.info("Deleting all memories")
        memory.reset()
        logger.info("All memories deleted successfully")
        return {"status": "memory deleted"}
    except Exception as e:
        logger.error(f"Error in delete_all_memories: {str(e)}")
        return {"status": "error", "message": str(e)}
