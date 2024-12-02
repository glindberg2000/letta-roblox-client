# Developer Notes

## Memory System
The memory system is key to NPC behavior:
- Memory blocks affect responses in real-time
- Updates must include full memory structure
- Memory influences conversation style and content

Example: A merchant NPC can shift from helping beginners to dealing in rare items by updating their memory blocks.

## Memory Structure
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

## Testing
Tests verify:
1. Memory updates work correctly
2. NPCs maintain context
3. Responses reflect personality
4. Memory influences behavior

Run tests with:
```bash
pytest -sv  # All tests
pytest -k test_name  # Specific test
```

## Common Issues
- Memory updates require proper structure
- Always clean up agents after use
- Verify memory influence through responses 