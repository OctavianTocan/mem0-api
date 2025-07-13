from agno.agent import Agent
from agno.models.gemini import Gemini
from agno.tools.reasoning import ReasoningTools
from mem0 import Memory
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MemoryEnhancedAgent:
    def __init__(self, memory_instance: Memory, model_name: str):
        self.memory = memory_instance
        self.agent = Agent(
            model=Gemini(id=model_name),
            tools=[ReasoningTools(add_instructions=True)],
            instructions="""You are a memory-enhanced AI assistant. 
            When responding, consider the provided memory context to give more informed and personalized responses.
            If the memory context is relevant, incorporate it naturally into your response.
            Be helpful, accurate, and conversational.""",
            markdown=True
        )
    
    def chat_with_memory(
        self, 
        query: str, 
        user_id: str, 
        agent_id: str, 
        store_conversation: bool = True,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Processing chat query for user: {user_id}, agent: {agent_id}")
            logger.info(f"Query: {query}")
            
            # Retrieve relevant memories
            memory_results = self.memory.search(
                query=query,
                user_id=user_id,
                agent_id=agent_id,
                limit=5
            )
            
            logger.info(f"Found {len(memory_results.get('results', []))} relevant memories")
            
            # Prepare enhanced prompt with memory context
            memory_context = self._format_memory_context(memory_results.get('results', []))
            enhanced_prompt = self._build_enhanced_prompt(query, memory_context)
            
            # Get agent response
            response = self.agent.run(enhanced_prompt)
            
            logger.info(f"Generated response: {response.content[:100]}...")
            
            # Optionally store the conversation in memory
            if store_conversation:
                self._store_conversation(query, response.content, user_id, agent_id, metadata or {})
            
            return {
                "response": response.content,
                "memories_used": len(memory_results.get('results', [])),
                "memory_context": memory_context if memory_results.get('results') else None
            }
            
        except Exception as e:
            logger.error(f"Error in chat_with_memory: {str(e)}")
            raise e
    
    def _format_memory_context(self, memories: list) -> str:
        if not memories:
            return ""
        
        context_parts = []
        for i, mem in enumerate(memories, 1):
            memory_text = mem.get('memory', '')
            if memory_text:
                context_parts.append(f"{i}. {memory_text}")
        
        return "\n".join(context_parts)
    
    def _build_enhanced_prompt(self, query: str, memory_context: str) -> str:
        if memory_context:
            return f"""
Relevant memories from previous conversations:
{memory_context}

Current user query: {query}

Please provide a helpful response considering both the current query and any relevant context from the memories above.
"""
        else:
            return f"""
User query: {query}

Please provide a helpful response to the user's query.
"""
    
    def _store_conversation(
        self, 
        query: str, 
        response: str, 
        user_id: str, 
        agent_id: str,
        metadata: Dict[str, Any]
    ):
        try:
            conversation_metadata = {
                "type": "conversation",
                "source": "agno_agent",
                **metadata
            }
            
            # Store as separate user and assistant messages
            messages = [
                {"role": "user", "content": query},
                {"role": "assistant", "content": response}
            ]
            
            self.memory.add(
                messages,
                user_id=user_id,
                agent_id=agent_id,
                metadata=conversation_metadata
            )
            
            logger.info(f"Stored conversation in memory for user: {user_id}")
            
        except Exception as e:
            logger.warning(f"Could not store conversation in memory: {e}")