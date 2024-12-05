"""Letta Roblox Client

A lightweight client for managing Letta AI agents as Roblox NPCs.
Supports both pip-installed (8333) and Docker (8283) servers.

Server Types:
    pip (8333):
        - Uses friendly agent names
        - Accepts full ChatMemory structure
        - Local timestamps

    docker (8283):
        - Uses timestamp-based names
        - Requires simpler memory structure
        - UTC timestamps

Examples:
    >>> from letta import ChatMemory
    >>> from letta_roblox.client import LettaRobloxClient
    
    # Pip server
    >>> client = LettaRobloxClient(port=8333, server_type="pip")
    >>> agent = client.create_agent(
    ...     memory=ChatMemory(
    ...         human="Player info",
    ...         persona="NPC personality"
    ...     )
    ... )
    
    # Docker server
    >>> client = LettaRobloxClient(port=8283, server_type="docker")
    >>> agent = client.create_agent(
    ...     memory=ChatMemory(
    ...         human="Player info",
    ...         persona="NPC personality"
    ...     )
    ... )
"""
import json
import time
import requests
import os
from typing import Dict, Optional, List, Union
from letta import (
    ChatMemory,
    LLMConfig,
    EmbeddingConfig,
    create_client
)

class LettaRobloxClient:
    """Client for managing Letta AI agents as Roblox NPCs.
    
    This client handles the differences between pip-installed and Docker servers:
    1. Memory structure differences
    2. Agent naming conventions
    3. Timestamp formats
    
    Examples:
        # Pip server (8333)
        client = LettaRobloxClient("http://localhost:8333")
        agent = client.create_agent(
            memory=ChatMemory(
                human="Player info",
                persona="NPC personality"
            )
        )
        
        # Docker server (8283)
        client = LettaRobloxClient("http://localhost:8283")
        agent = client.create_agent(
            memory=ChatMemory(
                human="Player info",
                persona="NPC personality"
            )
        )
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8333,
        server_type: str = "pip",
        protocol: str = "http"
    ):
        """Initialize client."""
        if server_type not in ["pip", "docker"]:
            raise ValueError("server_type must be either 'pip' or 'docker'")
        
        self.server_type = server_type
        self.base_url = f"{protocol}://{host}:{port}"
        self.headers = {'Content-Type': 'application/json'}
    
    def _convert_memory_for_docker(self, memory: Union[ChatMemory, Dict]) -> Dict:
        """Convert memory to Docker-compatible format.
        
        Docker server requires a simpler memory structure without extra fields.
        
        Args:
            memory: ChatMemory object or dict with memory structure
            
        Returns:
            Dict with Docker-compatible memory structure
        """
        if isinstance(memory, ChatMemory):
            return {
                "memory": {
                    "human": {
                        "value": memory.human,
                        "limit": 2000,
                        "label": "human",
                        "template": False
                    },
                    "persona": {
                        "value": memory.persona,
                        "limit": 2000,
                        "label": "persona",
                        "template": False
                    }
                }
            }
        return memory
    
    def create_agent(
        self,
        memory: Union[ChatMemory, Dict],
        name: Optional[str] = None,
        llm_config: Optional[Dict] = None,
        embedding_config: Optional[Dict] = None
    ) -> Dict:
        """Create a new agent."""
        # Convert ChatMemory to dict for both servers
        if isinstance(memory, ChatMemory):
            memory_dict = memory.dict()  # Get raw dict first
            print("\nDebug - Memory dict:", json.dumps(memory_dict, indent=2))
            
            # Add extra fields for pip server
            if not self.server_type == "docker":
                memory_dict["memory"]["human"].update({
                    "is_template": False,
                    "organization_id": None,
                    "created_by_id": None,
                    "last_updated_by_id": None
                })
                memory_dict["memory"]["persona"].update({
                    "is_template": False,
                    "organization_id": None,
                    "created_by_id": None,
                    "last_updated_by_id": None
                })
        else:
            memory_dict = memory

        # Generate unique name for Docker
        if self.server_type == "docker" and not name:
            name = f"agent_{int(time.time())}"
            
        payload = {
            "name": name,
            "memory": memory_dict
        }
        
        if llm_config:
            payload["llm_config"] = llm_config
        if embedding_config:
            payload["embedding_config"] = embedding_config
            
        response = requests.post(
            f"{self.base_url}/v1/agents",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

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

    def list_agents(self) -> List[Dict]:
        """List all agents."""
        url = f"{self.base_url}/v1/agents"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def delete_all_agents(self) -> None:
        """Delete all agents.
        
        Example:
            client = LettaRobloxClient()
            client.delete_all_agents()  # Cleanup everything
        """
        # Get all agents
        agents = self.list_agents()
        
        # Delete each agent
        for agent in agents:
            try:
                self.delete_agent(agent['id'])
                print(f"Deleted agent {agent['id']}")
            except Exception as e:
                print(f"Failed to delete agent {agent['id']}: {e}")