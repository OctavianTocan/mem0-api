from typing import List, Dict, Optional, Any
from models import AddMemoryInput

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
                       metadata: Dict[str, Any]) -> AddMemoryInput:
        """Create AddMemoryInput for storing raw transcript with infer=False"""
        return AddMemoryInput(
            messages=transcript,
            user_id=user_id,
            agent_id=agent_id,
            infer=False,
            metadata=metadata
        )

    def extract_memories(self,
                       transcript: List[Dict[str, str]],
                       user_id: str,
                       agent_id: str,
                       metadata: Dict[str, Any],
                       prompt: Optional[str] = None) -> AddMemoryInput:
        """Create AddMemoryInput for extracting and storing memories from transcript with infer=True"""
        return AddMemoryInput(
            messages=transcript,
            user_id=user_id,
            agent_id=agent_id,
            infer=True,
            metadata=metadata,
            prompt=prompt or self.transcript_prompt
        )
