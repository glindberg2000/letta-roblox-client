"""Tests for Letta REST API integration.

This module tests the core functionality needed for Roblox NPC integration:
1. Creating agents with memory blocks
2. Updating memory (both human and persona blocks)
3. Verifying memory updates
4. Proper cleanup of test agents

Each test uses fixtures for setup and cleanup to ensure test isolation.
"""
from letta import create_client
import time
import json
import requests
import pytest
from letta_roblox.client import LettaRobloxClient

@pytest.fixture
def client():
    """Create a test client for Letta API.
    
    Returns:
        client: Configured Letta client pointing to local Docker instance
    """
    return create_client(base_url="http://localhost:8283")

@pytest.fixture
def test_agent(client):
    """Create and manage a test agent lifecycle.
    
    This fixture:
    1. Creates an agent with default memory blocks
    2. Yields the agent for test use
    3. Cleans up the agent after test
    
    Args:
        client: Letta client fixture
    
    Yields:
        dict: Created agent details including ID
    """
    agent_name = f"test_agent_{int(time.time())}"
    url = f"{client.base_url}/v1/agents"
    
    payload = {
        "name": agent_name,
        "memory": {
            "memory": {
                "human": {
                    "value": "Initial human info",
                    "limit": 2000,
                    "name": "player_info",
                    "template": False,
                    "label": "human"
                },
                "persona": {
                    "value": "Initial persona info",
                    "limit": 2000,
                    "name": "npc_persona",
                    "template": False,
                    "label": "persona"
                }
            },
            "prompt_template": "{% for block in memory.values() %}<{{ block.label }}>\n{{ block.value }}\n</{{ block.label }}>{% endfor %}"
        },
        # Required model configs
        "llm_config": {
            "model": "letta-free",
            "model_endpoint_type": "openai",
            "model_endpoint": "https://inference.memgpt.ai",
            "context_window": 16384,
            "put_inner_thoughts_in_kwargs": True
        },
        "embedding_config": {
            "embedding_endpoint_type": "hugging-face",
            "embedding_endpoint": "https://embeddings.memgpt.ai",
            "embedding_model": "letta-free",
            "embedding_dim": 1024,
            "embedding_chunk_size": 300
        },
        # Required for messaging
        "system": "You are a helpful NPC in a Roblox game. Stay in character at all times.",
        "tools": ["send_message"],  # Required for responses
        "agent_type": "memgpt_agent"
    }

    response = requests.post(url, json=payload, headers=client.headers)
    response.raise_for_status()
    agent = response.json()
    
    yield agent
    
    client.delete_agent(agent['id'])

@pytest.fixture
def gpt4_agent(client):
    """Create and manage a GPT-4o-mini agent lifecycle."""
    agent_name = f"gpt4_agent_{int(time.time())}"
    url = f"{client.base_url}/v1/agents"
    
    payload = {
        "name": agent_name,
        "memory": {
            "memory": {
                "human": {
                    "value": "Initial human info",
                    "limit": 2000,
                    "name": "player_info",
                    "template": False,
                    "label": "human"
                },
                "persona": {
                    "value": "Initial persona info",
                    "limit": 2000,
                    "name": "npc_persona",
                    "template": False,
                    "label": "persona"
                }
            },
            "prompt_template": "{% for block in memory.values() %}<{{ block.label }}>\n{{ block.value }}\n</{{ block.label }}>{% endfor %}"
        },
        # GPT-4o-mini configuration
        "llm_config": {
            "model": "gpt-4o-mini",
            "model_endpoint_type": "openai",
            "model_endpoint": "https://api.openai.com/v1",
            "context_window": 128000,
            "put_inner_thoughts_in_kwargs": True
        },
        "embedding_config": {
            "embedding_endpoint_type": "openai",
            "embedding_endpoint": "https://api.openai.com/v1",
            "embedding_model": "text-embedding-ada-002",
            "embedding_dim": 1536,
            "embedding_chunk_size": 300
        },
        # Required for messaging
        "system": "You are a high-end merchant NPC in a Roblox game. Stay in character at all times.",
        "tools": ["send_message"],
        "agent_type": "memgpt_agent"
    }

    response = requests.post(url, json=payload, headers=client.headers)
    response.raise_for_status()
    agent = response.json()
    
    yield agent
    
    client.delete_agent(agent['id'])

def test_memory_updates(client, test_agent):
    """Test updating agent memory blocks.
    
    This test verifies that we can:
    1. Get current memory state
    2. Update human memory block
    3. Update persona memory block
    4. Verify both updates were successful
    
    The memory updates use the format required by Roblox NPCs:
    - Human block: Player information
    - Persona block: NPC personality
    
    Args:
        client: Letta client fixture
        test_agent: Agent fixture with memory blocks
    """
    agent_id = test_agent['id']

    # First get current memory
    memory_url = f"{client.base_url}/v1/agents/{agent_id}/memory"
    response = requests.request("GET", memory_url, headers=client.headers)
    current = response.json()
    print("\nCurrent memory:", json.dumps(current, indent=2))

    # Update human block with player info
    print("\nUpdating human block...")
    human_payload = {
        "human": "I am a Roblox player who loves adventures!"
    }
    human_response = requests.request("PATCH", memory_url, json=human_payload, headers=client.headers)
    human_response.raise_for_status()
    print("Human block updated")

    # Update persona block with NPC personality
    print("\nUpdating persona block...")
    persona_payload = {
        "persona": "I am a friendly NPC guide who helps players on their journey."
    }
    persona_response = requests.request("PATCH", memory_url, json=persona_payload, headers=client.headers)
    persona_response.raise_for_status()
    print("Persona block updated")

    # Verify both updates
    verify_response = requests.request("GET", memory_url, headers=client.headers)
    updated_memory = verify_response.json()
    print("\nUpdated memory:", json.dumps(updated_memory, indent=2))
    
    # Verify memory contains expected content
    assert "Roblox player" in updated_memory['memory']['human']['value']
    assert "friendly NPC guide" in updated_memory['memory']['persona']['value']

def test_gpt4_memory_updates(client, gpt4_agent):
    """Test memory updates with GPT-4o-mini agent.
    
    This test verifies memory operations work with OpenAI's GPT-4o-mini model.
    This is important for production NPCs that need higher quality responses.
    
    The test follows the same flow as the basic memory test but uses
    the GPT-4o-mini model configuration.
    
    Args:
        client: Letta client fixture
        gpt4_agent: GPT-4o-mini agent fixture
    """
    agent_id = gpt4_agent['id']

    # Get current memory
    memory_url = f"{client.base_url}/v1/agents/{agent_id}/memory"
    response = requests.request("GET", memory_url, headers=client.headers)
    current = response.json()
    print("\nCurrent GPT-4 memory:", json.dumps(current, indent=2))

    # Update human block
    human_payload = {
        "human": "I am a Roblox player exploring the trading district."
    }
    human_response = requests.request("PATCH", memory_url, json=human_payload, headers=client.headers)
    human_response.raise_for_status()
    print("Human block updated")

    # Update persona block
    persona_payload = {
        "persona": "I am a merchant NPC specializing in rare items."
    }
    persona_response = requests.request("PATCH", memory_url, json=persona_payload, headers=client.headers)
    persona_response.raise_for_status()
    print("Persona block updated")

    # Verify updates
    verify_response = requests.request("GET", memory_url, headers=client.headers)
    updated_memory = verify_response.json()
    print("\nUpdated GPT-4 memory:", json.dumps(updated_memory, indent=2))
    
    assert "trading district" in updated_memory['memory']['human']['value']
    assert "merchant NPC" in updated_memory['memory']['persona']['value']

def test_agent_messaging(client, test_agent):
    """Test free model agent messaging."""
    agent_id = test_agent['id']
    print("\n" + "="*50)
    print("FREE MODEL MESSAGING TEST")
    print("="*50)
    print(f"Agent ID: {agent_id}")

    # Set up memory
    memory_url = f"{client.base_url}/v1/agents/{agent_id}/memory"
    memory_updates = {
        "human": "I am a new Roblox player looking to trade items.",
        "persona": "I am a friendly merchant NPC who helps players trade items safely."
    }
    
    print("\n1. MEMORY SETUP")
    print("-"*30)
    for block, value in memory_updates.items():
        print(f"{block.upper()}: {value}")
        response = requests.request("PATCH", memory_url, json={block: value}, headers=client.headers)
        response.raise_for_status()

    # Send message
    messages_url = f"{client.base_url}/v1/agents/{agent_id}/messages"
    user_message = "Hello! Can you help me trade my items?"
    
    print("\n2. CONVERSATION")
    print("-"*30)
    print(f"USER: {user_message}")
    
    message_payload = {
        "messages": [{
            "role": "user",
            "text": user_message
        }],
        "return_message_object": True
    }
    
    try:
        response = requests.request("POST", messages_url, json=message_payload, headers=client.headers)
        response.raise_for_status()
        messages = response.json()
        print("\nRaw response:", json.dumps(messages, indent=2))

        # Process response
        agent_messages = [
            msg for msg in messages['messages'] 
            if msg['role'] == 'assistant' and msg.get('tool_calls')
        ]
        
        if len(agent_messages) > 0:
            print("\n3. NPC RESPONSE")
            print("-"*30)
            for msg in agent_messages:
                for call in msg['tool_calls']:
                    if call['function']['name'] == 'send_message':
                        response_text = json.loads(call['function']['arguments'])['message']
                        print(f"NPC: {response_text}")
                        key_words = ['trade', 'merchant', 'items', 'safe']
                        found_words = [word for word in key_words if word in response_text.lower()]
                        print(f"\nContext words found: {', '.join(found_words)}")
                        assert len(found_words) > 0, "Response should contain context words"
        else:
            raise AssertionError("No response received")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("Response content:", response.text)
        raise

    print("\n" + "="*50)

def test_gpt4_agent_messaging(client, gpt4_agent):
    """Test GPT-4 agent messaging."""
    agent_id = gpt4_agent['id']
    print("\n=== Testing GPT-4 Agent Messaging ===")
    print(f"Agent ID: {agent_id}")

    # Set up memory
    memory_url = f"{client.base_url}/v1/agents/{agent_id}/memory"
    memory_updates = {
        "human": "I am an experienced Roblox trader looking for rare collectibles.",
        "persona": "I am a high-level merchant NPC specializing in rare and valuable items."
    }
    
    print("\n1. Setting up GPT-4 memory:")
    for block, value in memory_updates.items():
        print(f"Updating {block}: {value}")
        response = requests.request("PATCH", memory_url, json={block: value}, headers=client.headers)
        response.raise_for_status()

    # Test multiple messages
    messages_url = f"{client.base_url}/v1/agents/{agent_id}/messages"
    test_messages = [
        "What rare items do you have in stock?",
        "I'm interested in limited edition items.",
        "How do you verify item authenticity?"
    ]
    
    for i, user_message in enumerate(test_messages, 1):
        print(f"\n--- GPT-4 Exchange {i} ---")
        print(f"User: {user_message}")
        
        message_payload = {
            "messages": [{
                "role": "user",
                "text": user_message
            }],
            "return_message_object": True
        }
        
        response = requests.request("POST", messages_url, json=message_payload, headers=client.headers)
        response.raise_for_status()
        messages = response.json()

        # Process response
        agent_messages = [
            msg for msg in messages['messages'] 
            if msg['role'] == 'assistant' and msg.get('tool_calls')
        ]
        
        if len(agent_messages) > 0:
            for msg in agent_messages:
                for call in msg['tool_calls']:
                    if call['function']['name'] == 'send_message':
                        response_text = json.loads(call['function']['arguments'])['message']
                        print(f"NPC (GPT-4): {response_text}")
                        # Log found context words
                        key_words = ['rare', 'items', 'limited', 'authentic']
                        found_words = [word for word in key_words if word in response_text.lower()]
                        print(f"Context words: {', '.join(found_words)}")
                        assert len(found_words) > 0
        else:
            raise AssertionError("No response received")
        
        print("-" * 50)

def test_roblox_client_wrapper():
    """Test the Roblox-specific client wrapper.
    
    This test verifies our high-level client wrapper works:
    1. Creates NPC agent with type-specific memory
    2. Sends messages and gets responses
    3. Cleans up properly
    """
    print("\n" + "="*50)
    print("TESTING ROBLOX CLIENT WRAPPER")
    print("="*50)
    
    # Initialize wrapper
    client = LettaRobloxClient("http://localhost:8283")
    
    # Create merchant NPC
    print("\n1. Creating merchant NPC...")
    agent = client.create_agent(
        npc_type="merchant",
        initial_memory={
            "human": "I am a new Roblox player looking to trade items.",
            "persona": "I am a friendly merchant NPC who helps players trade items safely."
        }
    )
    print(f"Agent created: {agent['id']}")
    
    try:
        # Test message exchange
        print("\n2. Testing conversation...")
        user_message = "Hello! Can you help me trade my items?"
        print(f"USER: {user_message}")
        
        response = client.send_message(agent['id'], user_message)
        print(f"NPC: {response}")
        
        # Verify response is contextual
        key_words = ['trade', 'merchant', 'items', 'safe']
        found_words = [word for word in key_words if word in response.lower()]
        print(f"\nContext words found: {', '.join(found_words)}")
        assert len(found_words) > 0, "Response should contain context words"
        
        print("\n3. Testing memory update...")
        client.update_memory(
            agent['id'],
            {
                "human": "Player has rare sword to trade",
                "persona": "I am a merchant interested in rare weapons"
            }
        )
        print("Memory updated successfully")
    
    finally:
        # Clean up
        print("\n4. Cleaning up...")
        client.delete_agent(agent['id'])
        print("Agent deleted")
    
    print("\n" + "="*50)

@pytest.mark.debug
def test_roblox_client_wrapper():
    """Test the Roblox-specific client wrapper."""
    print("\n=== Testing Roblox Client ===")
    
    client = LettaRobloxClient("http://localhost:8283")
    
    # Create merchant NPC
    print("\nCreating merchant NPC...")
    agent = client.create_agent(
        npc_type="merchant",
        initial_memory={
            "human": "I am a new Roblox player looking to trade items.",
            "persona": "I am a friendly merchant NPC who helps players trade items safely."
        }
    )
    print(f"Created agent: {agent['id']}")
    
    try:
        # Send message
        print("\nSending message...")
        message = "Hello! Can you help me trade my items?"
        print(f"USER: {message}")
        
        response = client.send_message(agent['id'], message)
        print(f"NPC: {response}")
        
        # Verify response
        key_words = ['trade', 'merchant', 'items']
        found_words = [word for word in key_words if word in response.lower()]
        print(f"\nFound context words: {', '.join(found_words)}")
        assert len(found_words) > 0, "Response should contain context words"
    
    finally:
        print("\nCleaning up...")
        client.delete_agent(agent['id'])
        print("Done!")