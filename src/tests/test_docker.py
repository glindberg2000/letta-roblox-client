import pytest
from letta import ChatMemory
from letta_roblox.client import LettaRobloxClient

@pytest.mark.docker
def test_docker_basic():
    """Test basic Docker server functionality."""
    client = LettaRobloxClient(base_url="http://localhost:8283")
    
    agent = client.create_agent(
        name="test_docker",
        memory=ChatMemory(
            human="Test human",
            persona="Test persona"
        )
    )
    
    try:
        assert agent is not None
        assert 'id' in agent
    finally:
        client.delete_agent(agent['id']) 