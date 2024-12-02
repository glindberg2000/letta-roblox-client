# Letta Integration Guide

## Core Functions

### 1. Create Agent
```python
agent = client.create_agent(
    npc_type="merchant",
    initial_memory={
        "human": "Player context here",
        "persona": "NPC personality here"
    }
)
```

### 2. Update Memory
```python
client.update_memory(agent['id'], {
    "human": "New player info",
    "persona": "New NPC personality"
})
```

### 3. Send Messages
```python
response = client.send_message(agent['id'], "Hello NPC!")
print(f"NPC: {response}")
```

### 4. Delete Agent
```python
client.delete_agent(agent['id'])
```

## Model Options

1. Free Model (Default)
```python
# Uses letta-free model
client = LettaRobloxClient("http://your-server:8283")
```

2. GPT-4 Model (Production)
```python
# Configure for GPT-4 in your server
client = LettaRobloxClient("http://your-server:8283")
```

## Best Practices
1. Always clean up agents after use
2. Validate NPC responses
3. Handle API errors gracefully
4. Monitor memory usage