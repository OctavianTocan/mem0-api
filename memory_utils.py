from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from mem0_api import AddMemoryInput

class TranscriptHandler:
    def __init__(self):
        self.transcript_prompt = (
            "Extract key insights, decisions, and action items from this meeting transcript. "
            "Focus on information that would be useful to remember long-term."
        )

    def store_transcript(self, 
                       transcript: List[Dict[str, str]],
                       user_id: str,
                       agent_id: str,
                       metadata: Dict[str, Any]) -> dict:
        """Store raw transcript with infer=False"""
        input = AddMemoryInput(
            messages=transcript,
            user_id=user_id,
            agent_id=agent_id,
            infer=False,
            metadata=metadata
        )
        from mem0_api import _add_memory_core
        return _add_memory_core(input)

    def extract_memories(self,
                       transcript: List[Dict[str, str]],
                       user_id: str,
                       agent_id: str,
                       metadata: Dict[str, Any],
                       prompt: Optional[str] = None) -> dict:
        """Extract and store memories from transcript with infer=True"""
        input = AddMemoryInput(
            messages=transcript,
            user_id=user_id,
            agent_id=agent_id,
            infer=True,
            metadata=metadata,
            prompt=prompt or self.transcript_prompt
        )
        from mem0_api import _add_memory_core
        return _add_memory_core(input)
