# Letta Roblox Client

A lightweight client for integrating Letta AI agents with Roblox NPCs.

## Installation

1. Add to your project's requirements.txt:
```
git+ssh://git@github.com/glindberg2000/letta-roblox-client.git@main#egg=letta_roblox&subdirectory=src
```

2. Or install directly:
```bash
pip install "git+ssh://git@github.com/glindberg2000/letta-roblox-client.git@main#egg=letta_roblox&subdirectory=src"
```

## Usage

### Python API
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

### Command Line Tool
The package includes a command-line tool for managing agents:

```bash
# List all agents
letta-manage list

# Show detailed agent info
letta-manage list -v

# Get specific agent
letta-manage get --id agent-123

# Delete agent
letta-manage delete --id agent-123

# Delete all agents
letta-manage delete-all
```

## Development

For contributors:
```bash
# Clone repo
git clone git@github.com:glindberg2000/letta-roblox-client.git
cd letta-roblox-client

# Install in development mode
cd src
pip install -e .

# Run tests
pytest -sv
```

## Documentation
- [Integration Guide](src/docs/letta_integration.md) - Detailed API usage
- [Developer Notes](src/docs/NOTES_TO_DEVS.md) - Implementation details
