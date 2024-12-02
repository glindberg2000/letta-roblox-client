# Letta Integration Guide for Roblox NPCs

## Overview
This guide explains how to integrate Letta's AI agents with Roblox NPCs using the REST API.

## Setup

1. Install dependencies:
```bash
pip install letta requests pytest
```

2. Configure environment:
```bash
# Required for tests
export LETTA_API_URL="http://localhost:8283"  # Local Docker
export OPENAI_API_KEY="your_key_here"         # For GPT-4 tests
```

## Running Tests
We provide comprehensive tests for both free and GPT-4 models:

```bash
# Run all tests with output
pytest -sv src/tests/test_letta.py

# Run specific test
pytest -sv src/tests/test_letta.py -k test_agent_messaging

# Run without GPT-4 tests
pytest -sv src/tests/test_letta.py -k "not gpt4"
```

## Core Functions

### 1. Create Agent
```python
# Create agent with memory blocks
payload = {
    "name": f"npc_{int(time.time())}",  # Unique name
    "memory": {
        "memory": {
            "human": {
                "value": "Initial player info",
                "limit": 2000,
                "name": "player_info",
                "template": False,
                "label": "human"
            },
            "persona": {
                "value": "I am a friendly NPC",
                "limit": 2000,
                "name": "npc_persona",
                "template": False,
                "label": "persona"
            }
        },
        "prompt_template": "{% for block in memory.values() %}<{{ block.label }}>\n{{ block.value }}\n</{{ block.label }}>{% endfor %}"
    },
    # Required for messaging
    "system": "You are a helpful NPC in a Roblox game. Stay in character at all times.",
    "tools": ["send_message"],
    "agent_type": "memgpt_agent"
}

response = requests.post(f"{base_url}/v1/agents", json=payload, headers=headers)
agent_id = response.json()['id']
```

### 2. Update Memory
```python
# Update player info
human_payload = {
    "human": "New player information"
}
requests.patch(f"{base_url}/v1/agents/{agent_id}/memory", 
              json=human_payload, headers=headers)

# Update NPC personality
persona_payload = {
    "persona": "New NPC personality"
}
requests.patch(f"{base_url}/v1/agents/{agent_id}/memory", 
              json=persona_payload, headers=headers)
```

### 3. Send Messages
```python
# Send message to NPC
message_payload = {
    "messages": [{
        "role": "user",
        "text": "Hello NPC!"
    }],
    "return_message_object": True
}

response = requests.post(f"{base_url}/v1/agents/{agent_id}/messages", 
                        json=message_payload, headers=headers)

# Extract NPC response
messages = response.json()
for msg in messages['messages']:
    if msg['role'] == 'assistant' and msg.get('tool_calls'):
        for call in msg['tool_calls']:
            if call['function']['name'] == 'send_message':
                npc_response = json.loads(call['function']['arguments'])['message']
                print(f"NPC: {npc_response}")
```

### 4. Delete Agent
```python
requests.delete(f"{base_url}/v1/agents/{agent_id}", headers=headers)
```

## Model Options

1. Free Model (Default)
```python
"llm_config": {
    "model": "letta-free",
    "model_endpoint_type": "openai",
    "model_endpoint": "https://inference.memgpt.ai",
    "context_window": 16384
}
```

2. GPT-4 Model (Production)
```python
"llm_config": {
    "model": "gpt-4o-mini",
    "model_endpoint_type": "openai",
    "model_endpoint": "https://api.openai.com/v1",
    "context_window": 128000
}
```

## Testing
Our test suite (`test_letta.py`) verifies:
1. Agent creation and deletion
2. Memory updates
3. Message handling
4. Response validation

Run with output:
```bash
pytest -sv src/tests/test_letta.py
```

## Best Practices
1. Always clean up agents after use
2. Validate NPC responses
3. Handle API errors gracefully
4. Monitor memory usage