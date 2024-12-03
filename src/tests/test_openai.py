import pytest
from letta import ChatMemory, LLMConfig, EmbeddingConfig
from letta_roblox.client import LettaRobloxClient

@pytest.fixture
def gpt4o_config():
    """Config for GPT-4o-mini through Letta."""
    return {
        "llm": LLMConfig(
            model="gpt-4o-mini",
            model_endpoint_type="openai",
            model_endpoint="https://api.openai.com/v1",
            context_window=128000
        ),
        "embedding": EmbeddingConfig(
            embedding_endpoint_type="openai",
            embedding_endpoint="https://api.openai.com/v1",
            embedding_model="text-embedding-ada-002",
            embedding_dim=1536,
            embedding_chunk_size=300
        )
    }

def test_gpt4o_basic(gpt4o_config):
    """Test with GPT-4o-mini."""
    client = LettaRobloxClient()
    
    agent = client.create_agent(
        name="test_gpt4o",
        memory=ChatMemory(
            human="I am looking for rare items",
            persona="I am an expert merchant specializing in rare collectibles"
        ),
        llm_config=gpt4o_config["llm"],
        embedding_config=gpt4o_config["embedding"]
    )
    
    try:
        # Test advanced reasoning
        response = client.send_message(
            agent['id'],
            "What makes you an expert in rare items?"
        )
        assert len(response) > 200  # Expect detailed response
        
        # Test memory updates
        client.update_memory(
            agent['id'],
            {
                "human": "Player has successfully traded 10 rare items",
                "persona": "I am impressed by the player's trading expertise"
            }
        )
        
        # Test contextual awareness
        response = client.send_message(
            agent['id'],
            "What do you think of my trading history?"
        )
        assert "10 rare items" in response
        
    finally:
        client.delete_agent(agent['id']) 