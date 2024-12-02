# Notes on Letta Roblox Client Integration

## To the Lead Developer

This client library provides a clean REST API interface for managing Letta AI agents. Key points:

1. **Minimal Dependencies**: Only requires `requests` and `letta` packages
2. **Test Coverage**: Includes tests for both free and GPT-4 models
3. **Memory Management**: Structured for Roblox's player-NPC interaction model
4. **Error Handling**: Built-in validation and cleanup

The test suite (`test_letta.py`) demonstrates all core functionality and can serve as implementation examples.

## To the Roblox Developer

This client is designed to support NPC interactions in Roblox. Suggested integration points:

1. **Agent Lifecycle**:
   - Create agents when NPCs spawn
   - Update memory as players interact
   - Clean up agents when NPCs despawn

2. **Memory Structure**:
   ```python
   # Player info goes in human block
   human_block = {
       "human": "PlayerName: John, Level: 5, Location: Trading District"
   }
   
   # NPC personality goes in persona block
   persona_block = {
       "persona": "I am a friendly merchant specializing in rare items"
   }
   ```

3. **Quick Start**:
   ```python
   # 1. Create NPC agent
   agent = create_agent(npc_type="merchant")
   
   # 2. Update with player info
   update_memory(agent.id, player_info)
   
   # 3. Handle player message
   response = send_message(agent.id, player_message)
   
   # 4. Clean up when done
   delete_agent(agent.id)
   ```

The test suite shows working examples of all these operations with both free and GPT-4 models.

## Getting Started

1. Clone the repo:
```bash
git clone https://github.com/glindberg2000/letta-roblox-client.git
cd letta-roblox-client
```

2. Run tests (with output):
```bash
pytest -sv src/tests/test_letta.py
```

3. Check `src/docs/letta_integration.md` for full API details

Feel free to reach out with any questions about the client implementation or integration approaches. 