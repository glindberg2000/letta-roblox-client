from letta import ChatMemory
from letta_roblox.client import LettaRobloxClient
import json
import pytest
import os

@pytest.mark.pip
def test_pip_server():
    """Test against pip installed server."""
    client = LettaRobloxClient(base_url="http://localhost:8333")
    
    agent = client.create_agent(
        npc_type="test",
        memory=ChatMemory(
            human="Test human memory",
            persona="Test persona memory"
        )
    )
    
    try:
        assert agent is not None
        assert 'id' in agent
    finally:
        client.delete_agent(agent['id'])

def test_memory_get():
    """Test getting memory contents."""
    client = LettaRobloxClient()
    
    # Create agent with specific memory
    memory = ChatMemory(
        human="I am a new player named Alex.",
        persona="I am a friendly merchant named Sam."
    )
    
    agent = client.create_agent(
        npc_type="merchant",
        memory=memory
    )
    
    try:
        # Get memory structure
        memory_data = client.get_memory(agent['id'])
        
        # Verify memory structure
        assert 'memory' in memory_data
        assert 'human' in memory_data['memory']
        assert 'persona' in memory_data['memory']
        assert memory_data['memory']['human']['value'] == "I am a new player named Alex."
        
    finally:
        client.delete_agent(agent['id'])

def test_memory_update():
    """Test memory updating."""
    client = LettaRobloxClient()
    
    # Create agent
    agent = client.create_agent(
        npc_type="merchant",
        memory=ChatMemory(
            human="Original human memory",
            persona="Original persona memory"
        )
    )
    
    try:
        # Update memory
        client.update_memory(
            agent['id'],
            {
                "human": "Updated human memory",
                "persona": "Updated persona memory"
            }
        )
        
        # Verify update
        memory_data = client.get_memory(agent['id'])
        assert memory_data['memory']['human']['value'] == "Updated human memory"
        assert memory_data['memory']['persona']['value'] == "Updated persona memory"
        
    finally:
        client.delete_agent(agent['id'])

def test_send_message():
    """Test sending messages to agent."""
    client = LettaRobloxClient()
    
    # Create merchant NPC with specific personality
    agent = client.create_agent(
        npc_type="merchant",
        memory=ChatMemory(
            human="I am a new player looking to trade items.",
            persona="I am a friendly merchant who helps new players trade safely. I always verify items and give fair prices."
        )
    )
    
    try:
        # Send message and verify response
        response = client.send_message(
            agent['id'],
            "Hello! Can you help me trade my items?"
        )
        
        # Response should contain trading-related terms
        assert any(word in response.lower() for word in ['trade', 'items', 'help', 'safe'])
        
        # Update memory to change personality
        client.update_memory(
            agent['id'],
            {
                "human": "I am an experienced trader with rare items.",
                "persona": "I am a merchant specializing in rare and valuable items."
            }
        )
        
        # Send another message
        response = client.send_message(
            agent['id'],
            "What kind of items do you deal in?"
        )
        
        # Response should now contain terms about rare items
        assert any(word in response.lower() for word in ['rare', 'valuable', 'special'])
        
    finally:
        client.delete_agent(agent['id'])

def test_free_agent(free_config):
    """Test with free endpoints."""
    client = LettaRobloxClient()
    agent = client.create_agent(
        npc_type="test",
        memory=ChatMemory(
            human="I am a new player testing the free endpoint",
            persona="I am a test NPC using the free model"
        ),
        llm_config=free_config["llm"],
        embedding_config=free_config["embedding"]
    )
    
    try:
        # Test basic functionality
        response = client.send_message(agent['id'], "Hello!")
        assert response is not None
    finally:
        client.delete_agent(agent['id'])

def test_openai_agent(openai_config):
    """Test with OpenAI endpoints."""
    # Set OpenAI key from environment
    os.environ['OPENAI_API_KEY'] = 'your-key-here'  # For testing only
    
    client = LettaRobloxClient()
    agent = client.create_agent(
        npc_type="test",
        memory=ChatMemory(
            human="I am a player using the OpenAI endpoint",
            persona="I am a test NPC using GPT-4o-mini"
        ),
        llm_config=openai_config["llm"],
        embedding_config=openai_config["embedding"]
    )
    
    try:
        # Test basic functionality
        response = client.send_message(agent['id'], "Hello!")
        assert response is not None
        
        # Test GPT-4o specific capabilities
        response = client.send_message(
            agent['id'], 
            "Can you demonstrate your advanced reasoning?"
        )
        assert len(response) > 100  # Expect longer, more detailed responses
        
    finally:
        client.delete_agent(agent['id'])

@pytest.mark.docker
def test_docker_server():
    """Test against Docker server."""
    client = LettaRobloxClient(base_url="http://localhost:8283")
    
    # Create agent with Docker-specific memory structure
    memory = {
        "memory": {
            "human": {"value": "Test human", "limit": 2000},
            "persona": {"value": "Test persona", "limit": 2000}
        }
    }
    
    agent = client.create_agent_docker(
        npc_type="test",
        memory=memory
    )
    
    try:
        assert agent is not None
        assert 'id' in agent
        
        # Test memory structure
        memory_data = client.get_memory(agent['id'])
        assert memory_data['memory']['human']['value'] == "Test human"
        
    finally:
        client.delete_agent(agent['id'])