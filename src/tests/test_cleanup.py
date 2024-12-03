import pytest
from letta import ChatMemory
from letta_roblox.client import LettaRobloxClient

def test_delete_all_agents():
    """Test deleting all agents."""
    client = LettaRobloxClient()
    
    # Create some test agents
    agents = []
    for i in range(3):
        agent = client.create_agent(
            name=f"test_agent_{i}",
            memory=ChatMemory(
                human=f"Test human {i}",
                persona=f"Test persona {i}"
            )
        )
        agents.append(agent)
    
    # Verify agents exist
    all_agents = client.list_agents()
    assert len(all_agents) >= len(agents)
    
    # Delete all
    client.delete_all_agents()
    
    # Verify deletion
    remaining = client.list_agents()
    assert len([a for a in remaining if a['id'] in [ag['id'] for ag in agents]]) == 0 