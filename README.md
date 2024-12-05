# Letta Roblox Client

A lightweight client for managing Letta AI agents as Roblox NPCs.

## Installation

```bash
pip install letta-roblox
```

## Server Types
The client supports two server types:

### Pip Server (8333)

```python
client = LettaRobloxClient(
    host="localhost",
    port=8333,
    server_type="pip"  # Default
)
```
- Uses friendly agent names
- Accepts full ChatMemory structure
- Local timestamps

### Docker Server (8283)

```python
client = LettaRobloxClient(
    host="localhost",
    port=8283,
    server_type="docker"
)
```
- Uses timestamp-based names
- Requires simpler memory structure
- UTC timestamps

## Usage Examples

### Create Agent

```python
from letta import ChatMemory
from letta_roblox.client import LettaRobloxClient

# Works with both servers
client = LettaRobloxClient(port=8333)  # or port=8283
agent = client.create_agent(
    memory=ChatMemory(
        human="Player info",
        persona="NPC personality"
    )
)
```

### Command Line Tool

```bash
# List agents
letta-manage --host localhost --port 8333 list

# Get agent details
letta-manage --host localhost --port 8333 get --id <agent-id>

# Delete agent
letta-manage --host localhost --port 8333 delete --id <agent-id>
```

## Breaking Changes
Version 0.2.0:
- Changed server URL handling to use host/port
- Added explicit server_type parameter
- Removed deprecated URL format

## Migration Guide
From 0.1.x:

```python
# Old
client = LettaRobloxClient("http://localhost:8333")

# New
client = LettaRobloxClient(
    host="localhost",
    port=8333,
    server_type="pip"  # or "docker"
)
```
