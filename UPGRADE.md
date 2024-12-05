# Upgrade Guide

## 0.1.x to 0.2.0

### Breaking Changes
1. Server URL handling changed to use host/port
2. Added required server_type parameter
3. Removed deprecated URL format

### Migration Steps
1. Update client initialization:
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

2. Update CLI commands:
   ```bash
   # Old
   letta-manage --server http://localhost:8333 list

   # New
   letta-manage --host localhost --port 8333 list
   ```

3. Verify server type:
   - Use server_type="pip" for port 8333
   - Use server_type="docker" for port 8283

## Version 0.2.0

### Breaking Changes
1. Initialization Changes
   ```python
   # Old way
   client = LettaRobloxClient()  # Always initialized database
   
   # New way
   client = LettaRobloxClient()  # API-only by default
   client = LettaRobloxClient(skip_init=False)  # Full initialization
   ```

2. Docker Support
   ```python
   # Old way
   client.create_agent_docker(...)  # Removed
   
   # New way - use config
   client.create_agent(
       llm_config=LLMConfig(...),
       embedding_config=EmbeddingConfig(...)
   )
   ```

### New Features
1. Agent Cleanup
   ```python
   # List all agents
   agents = client.list_agents()
   
   # Delete all agents
   client.delete_all_agents()
   ```

2. Lazy Initialization
   - Database only initialized when needed
   - No ~/.letta/ created for API-only usage
   - Faster import times

### Migration Steps
1. Update imports:
   ```python
   from letta import ChatMemory, LLMConfig  # From letta package
   from letta_roblox.client import LettaRobloxClient
   ```

2. Update Docker usage:
   ```python
   # Replace create_agent_docker with create_agent + config
   ```

3. Test initialization:
   ```python
   # For API-only usage
   client = LettaRobloxClient()  # Default now
   
   # For full features
   client = LettaRobloxClient(skip_init=False)
   ``` 