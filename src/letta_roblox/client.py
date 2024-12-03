"""Letta Roblox Client

A lightweight client for managing Letta AI agents as Roblox NPCs.
"""
import json
import time
import requests
import os
from typing import Dict, Optional
from letta import ChatMemory, EmbeddingConfig, LLMConfig, create_client

class LettaRobloxClient:
    """Client for managing Letta AI agents as Roblox NPCs.
    
    This client provides a simplified interface for:
    1. Creating NPCs with specific roles
    2. Managing NPC memory and personality
    3. Handling player-NPC conversations
    4. Automatic cleanup of resources
    
    Memory Structure:
        The Letta API uses memory blocks for context:
        - human: Information about the player/user
        - persona: The NPC's personality and role
        
    Example:
        client = LettaRobloxClient("http://localhost:8283")
        agent = client.create_agent(
            npc_type="merchant",
            initial_memory={
                "human": "Player is new to trading",
                "persona": "I am a friendly merchant who helps new players trade safely"
            }
        )
    """
    
    def __init__(self, base_url: str = "http://localhost:8333"):
        """Initialize client."""
        self.base_url = base_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}
        self.client = create_client(base_url=self.base_url)

    def create_agent(self, npc_type: str, memory: ChatMemory, llm_config=None, embedding_config=None) -> Dict:
        """Create a new NPC agent."""
        client = create_client(base_url=self.base_url)
        
        # Use provided configs or defaults
        llm = llm_config or LLMConfig(
            model="letta-free",
            model_endpoint_type="openai",
            model_endpoint="https://inference.memgpt.ai",
            context_window=16384
        )
        
        embedding = embedding_config or EmbeddingConfig(
            embedding_endpoint_type="hugging-face",
            embedding_endpoint="https://embeddings.memgpt.ai",
            embedding_model="letta-free",
            embedding_dim=1024,
            embedding_chunk_size=300
        )
        
        agent_state = client.create_agent(
            name=f"npc_{npc_type}_{int(time.time())}",
            memory=memory,
            llm_config=llm,
            embedding_config=embedding
        )
        
        return agent_state.model_dump()

    def update_memory(self, agent_id: str, memory_updates: Dict[str, str]) -> None:
        """Update agent memory blocks.
        
        Args:
            agent_id: Agent ID to update
            memory_updates: Dict with "human" and/or "persona" values to update
        """
        url = f"{self.base_url}/v1/agents/{agent_id}/memory"
        
        # Send just the string values
        payload = {
            key: value
            for key, value in memory_updates.items()
            if key in ["human", "persona"]
        }
        
        response = requests.patch(url, json=payload, headers=self.headers)
        response.raise_for_status()

    def send_message(self, agent_id: str, message: str) -> str:
        """Send message to agent and get response.
        
        Args:
            agent_id: Agent ID to message
            message: Message text to send
            
        Returns:
            NPC's response text
            
        Example:
            response = client.send_message(agent_id, "What items do you have?")
            print(f"NPC: {response}")
        """
        url = f"{self.base_url}/v1/agents/{agent_id}/messages"
        
        payload = {
            "messages": [{
                "role": "user",
                "text": message
            }],
            "return_message_object": True
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        messages = response.json()
        
        # Extract NPC response
        for msg in messages['messages']:
            if msg['role'] == 'assistant' and msg.get('tool_calls'):
                for call in msg['tool_calls']:
                    if call['function']['name'] == 'send_message':
                        return json.loads(call['function']['arguments'])['message']
        
        raise ValueError("No response received from agent")

    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent."""
        url = f"{self.base_url}/v1/agents/{agent_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

    def get_memory(self, agent_id: str) -> Dict:
        """Get raw memory structure for an agent."""
        url = f"{self.base_url}/v1/agents/{agent_id}/memory"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_agent_docker(self, npc_type: str, memory: Dict) -> Dict:
        """Create agent specifically for Docker server."""
        client = create_client(base_url=self.base_url)
        
        agent_state = client.create_agent(
            name=f"npc_{npc_type}_{int(time.time())}",
            memory=memory,
            llm_config=LLMConfig(
                model="letta-free",
                model_endpoint_type="openai",
                model_endpoint="https://inference.memgpt.ai",
                context_window=16384
            ),
            embedding_config=EmbeddingConfig(
                embedding_endpoint_type="hugging-face",
                embedding_endpoint="https://embeddings.memgpt.ai",
                embedding_model="letta-free",
                embedding_dim=1024,
                embedding_chunk_size=300
            )
        )
        
        return agent_state.model_dump()