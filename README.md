# Letta Roblox Client

REST API client for integrating Letta AI agents with Roblox NPCs.

## Installation

1. Add to your project's requirements.txt:
```
git+https://github.com/your-org/letta-roblox-client.git@main
```

2. Or install directly:
```bash
pip install git+https://github.com/your-org/letta-roblox-client.git@main
```

## Quick Start

```python
from letta_roblox.client import LettaRobloxClient

# Initialize client
client = LettaRobloxClient("http://your-letta-server:8283")

# Create merchant NPC
agent = client.create_agent(
    npc_type="merchant",
    initial_memory={
        "human": "I am a new player who only has basic items.",
        "persona": "I am a merchant who specializes in helping new players."
    }
)

# Send message
response = client.send_message(agent['id'], "What items do you have?")
print(f"NPC: {response}")

# Update NPC personality
client.update_memory(agent['id'], {
    "human": "I am an experienced player with rare items.",
    "persona": "I am a merchant who deals in rare and valuable items."
})

# Clean up
client.delete_agent(agent['id'])
```

## Documentation
- [Integration Guide](src/docs/letta_integration.md) - Detailed API usage
- [Developer Notes](src/docs/NOTES_TO_DEVS.md) - Implementation details

## Development

For contributors:
```bash
git clone https://github.com/your-org/letta-roblox-client.git
cd letta-roblox-client
pip install -e .
pytest -sv  # Run tests
```
