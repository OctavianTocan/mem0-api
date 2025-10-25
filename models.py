from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class SearchInput(BaseModel):
    # The search query string
    query: str
    # The ID of the user performing the search, defaults to DEFAULT_USER_ID
    user_id: Optional[str] = None
    # Optional ID of the agent associated with the search
    agent_id: Optional[str] = None


class AddMemoryInput(BaseModel):
    # A list of message dictionaries to be added as memories
    messages: List[Dict[str, str]]
    # The ID of the user associated with these memories
    user_id: Optional[str] = None
    # Optional ID of the agent associated with these memories
    agent_id: Optional[str] = None
    # Boolean indicating whether to infer additional memories from the input
    infer: bool = True
    # Optional metadata dictionary for the memories
    metadata: Dict[str, Any] = {}
    # Optional prompt to guide memory inference
    prompt: Optional[str] = None


class GetAllMemoriesInput(BaseModel):
    # The ID of the user whose memories are to be retrieved
    user_id: str