# API Reference

## LettaRobloxClient

### Initialization
```python
client = LettaRobloxClient(base_url: str = "http://localhost:8333")
```

### Methods

#### create_agent()
Creates a new NPC agent.
```python
def create_agent(
    self, 
    npc_type: str,
    memory: ChatMemory,
    llm_config: Optional[LLMConfig] = None,
    embedding_config: Optional[EmbeddingConfig] = None
) -> Dict
```

#### send_message()
Sends a message to an agent.
```python
def send_message(self, agent_id: str, message: str) -> str
```

#### update_memory()
Updates agent memory.
```python
def update_memory(self, agent_id: str, memory_updates: Dict[str, str]) -> None
```

#### delete_agent()
Deletes an agent.
```python
def delete_agent(self, agent_id: str) -> None
``` 