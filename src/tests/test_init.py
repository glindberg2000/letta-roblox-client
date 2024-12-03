import pytest
from letta import ChatMemory
from letta_roblox.client import LettaRobloxClient

def test_api_only_init():
    """Test API-only initialization (default)."""
    client = LettaRobloxClient()  # skip_init=True by default
    
    agent = client.create_agent(
        name="test_api_only",
        memory=ChatMemory(
            human="Test human",
            persona="Test persona"
        )
    )
    
    try:
        assert agent is not None
        assert 'id' in agent
        
        # Test basic functionality
        response = client.send_message(agent['id'], "Hello!")
        assert response is not None
    finally:
        client.delete_agent(agent['id'])

def test_full_init():
    """Test full initialization with config."""
    client = LettaRobloxClient(skip_init=False)
    
    agent = client.create_agent(
        name="test_full_init",
        memory=ChatMemory(
            human="Test human",
            persona="Test persona"
        )
    )
    
    try:
        assert agent is not None
        assert 'id' in agent
        
        # Test basic functionality
        response = client.send_message(agent['id'], "Hello!")
        assert response is not None
    finally:
        client.delete_agent(agent['id']) 