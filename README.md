# Letta Roblox Client

A lightweight client for managing Letta AI agents as Roblox NPCs.

## Installation
```bash
pip install letta-roblox-client
```

## Server Setup
The client requires a running Letta server. Set up as a service:

```bash
# Create service file
sudo nano /etc/systemd/system/letta.service

[Unit]
Description=Letta AI Server
After=network.target

[Service]
Type=simple
User=your_user
Environment=OPENAI_API_KEY=your_key_here
Environment=OPENAI_BASE_URL=https://api.openai.com/v1
WorkingDirectory=/path/to/letta-deployment
ExecStart=/path/to/venv/bin/letta server --port 8333
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable letta
sudo systemctl start letta
```

## Usage

### Basic Usage
```python
from letta_roblox.client import LettaRobloxClient
from letta import ChatMemory

# Initialize client (defaults to http://localhost:8333)
client = LettaRobloxClient()

# Create NPC with free model (default)
agent = client.create_agent(
    npc_type="merchant",
    memory=ChatMemory(
        human="I am a new player looking to trade",
        persona="I am a friendly merchant who helps new traders"
    )
)

# Create NPC with GPT-4o-mini
agent = client.create_agent(
    npc_type="merchant",
    memory=ChatMemory(
        human="I am looking for rare items",
        persona="I am an expert merchant specializing in rare collectibles"
    ),
    llm_config=LLMConfig(
        model="gpt-4o-mini",
        model_endpoint_type="openai",
        model_endpoint="https://api.openai.com/v1",
        context_window=128000
    )
)

# Send message
response = client.send_message(agent['id'], "What items do you have?")

# Update memory
client.update_memory(
    agent['id'],
    {
        "human": "Player has completed 5 trades",
        "persona": "I give bonuses to experienced traders"
    }
)

# Cleanup
client.delete_agent(agent['id'])
```

### Configuration
```python
# Custom server
client = LettaRobloxClient(base_url="http://your-server:8333")

# Environment variables
LETTA_SERVER_URL=http://localhost:8333  # Server URL
OPENAI_API_KEY=your_key_here           # For GPT-4o-mini
```

## Development

```bash
# Clone repo
git clone <repo_url>
cd letta-roblox-client

# Install dependencies
cd src
pip install -e .

# Run tests
pytest -sv tests/  # All tests
pytest -sv tests/test_basic.py  # Basic tests
pytest -sv tests/test_openai.py  # GPT-4o tests
```

## Documentation
- [API Reference](docs/API.md)
- [Server Setup](docs/SERVER.md)
- [Development Guide](docs/DEVELOPMENT.md)
