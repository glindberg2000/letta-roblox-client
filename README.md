# Letta Roblox Client

REST API client for integrating Letta AI agents with Roblox NPCs.

## Installation

1. Add to your project's requirements.txt:
```
git+ssh://git@github.com/glindberg2000/letta-roblox-client.git@main#egg=letta_roblox&subdirectory=src
```

2. Or install directly:
```bash
pip install "git+ssh://git@github.com/glindberg2000/letta-roblox-client.git@main#egg=letta_roblox&subdirectory=src"
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

# Clean up
client.delete_agent(agent['id'])
```

## Documentation
- [Integration Guide](src/docs/letta_integration.md) - Detailed API usage
- [Developer Notes](src/docs/NOTES_TO_DEVS.md) - Implementation details

## Development

For contributors:
```bash
git clone git@github.com:glindberg2000/letta-roblox-client.git
cd letta-roblox-client
pip install -e .
pytest -sv  # Run tests
```

## Project Structure
```
letta-roblox-client/
├── README.md
└── src/
    ├── setup.py
    ├── letta_roblox/
    │   ├── __init__.py
    │   └── client.py
    ├── tests/
    │   └── test_letta.py
    └── docs/
        ├── letta_integration.md
        └── NOTES_TO_DEVS.md
```
