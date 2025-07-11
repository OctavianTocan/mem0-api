from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "default-researcher-id")
DEFAULT_AGENT_ID = os.getenv("DEFAULT_AGENT_ID", "default-agent-id")


class SearchInput(BaseModel):
    query: str
    user_id: str = DEFAULT_USER_ID
    agent_id: Optional[str] = None


class AddMemoryInput(BaseModel):
    messages: List[Dict[str, str]]
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    infer: bool = True
    metadata: Dict[str, Any] = {}
    prompt: Optional[str] = None


class AddTranscriptInput(BaseModel):
    transcript: List[Dict[str, str]]
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    extract_memories: bool = True
    prompt: Optional[str] = None
