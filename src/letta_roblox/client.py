"""Letta Roblox Client

A lightweight client for managing Letta AI agents as Roblox NPCs.
"""
import json
import time
import requests
from typing import Dict, Optional

class LettaRobloxClient:
    """Client for managing Letta AI agents as Roblox NPCs."""
    
    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        """Initialize client."""
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {'Content-Type': 'application/json'}

    def create_agent(self, npc_type: str, initial_memory: Optional[Dict] = None) -> Dict:
        """Create a new NPC agent.
        
        Args:
            npc_type: Type of NPC (e.g. "merchant", "guard")
            initial_memory: Optional initial memory blocks
            
        Example:
            agent = client.create_agent(
                npc_type="merchant",
                initial_memory={
                    "human": "I am a new player who only has basic items.",
                    "persona": "I am a merchant who specializes in helping new players."
                }
            )
        """
        memory = initial_memory or {
            "human": "New player",
            "persona": f"I am a {npc_type} NPC"
        }
        
        payload = {
            "name": f"{npc_type}_{int(time.time())}",
            "memory": {
                "human": {
                    "value": memory["human"],
                    "limit": 2000,
                    "name": "player_info",
                    "template": False,
                    "label": "human"
                },
                "persona": {
                    "value": memory["persona"],
                    "limit": 2000,
                    "name": "npc_persona",
                    "template": False,
                    "label": "persona"
                },
                "prompt_template": "{% for block in memory.values() %}<{{ block.label }}>\n{{ block.value }}\n</{{ block.label }}>{% endfor %}"
            },
            "system": f"You are a {npc_type} NPC in a Roblox game. Stay in character at all times.",
            "tools": ["send_message"],
            "agent_type": "memgpt_agent",
            "llm_config": {
                "model": "letta-free",
                "model_endpoint_type": "openai",
                "model_endpoint": "https://inference.memgpt.ai",
                "context_window": 16384,
                "put_inner_thoughts_in_kwargs": True
            },
            "embedding_config": {
                "embedding_endpoint_type": "hugging-face",
                "embedding_endpoint": "https://embeddings.memgpt.ai",
                "embedding_model": "letta-free",
                "embedding_dim": 1024,
                "embedding_chunk_size": 300
            }
        }
        
        response = requests.post(
            f"{self.base_url}/v1/agents",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_memory(self, agent_id: str, memory_updates: Dict[str, str]) -> None:
        """Update agent memory blocks."""
        url = f"{self.base_url}/v1/agents/{agent_id}/memory"
        
        # Build full memory structure
        payload = {"memory": {}}
        
        for block, value in memory_updates.items():
            if block not in ["human", "persona"]:
                continue
            
            payload["memory"][block] = {
                "value": value,
                "limit": 2000,
                "name": f"{block}_info",
                "template": False,
                "label": block
            }
        
        # Update memory
        response = requests.patch(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        # Verify update (optional but helpful for debugging)
        check = requests.get(url, headers=self.headers)
        print(f"\nVerified memory update:")
        print(json.dumps(check.json(), indent=2))

    def send_message(self, agent_id: str, message: str) -> str:
        """Send message to agent and get response."""
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