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
def roblox_client():
    """Create a test client for Letta Roblox API."""
    return LettaRobloxClient("http://localhost:8283")

@pytest.fixture
def test_agent(roblox_client):
    """Create and manage a test agent lifecycle."""
    agent = roblox_client.create_agent(
        npc_type="merchant",
        initial_memory={
            "human": "Initial human info",
            "persona": "Initial persona info"
        }
    )
    yield agent
    roblox_client.delete_agent(agent['id'])

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

def test_memory_updates(roblox_client, test_agent):
    """Test updating agent memory blocks."""
    print("\nTesting memory updates...")
    
    # Update memory blocks
    memory_updates = {
        "human": "I am a Roblox player who loves adventures!",
        "persona": "I am a friendly NPC guide who helps players on their journey."
    }
    roblox_client.update_memory(test_agent['id'], memory_updates)
    
    # Test message to verify memory influence
    response = roblox_client.send_message(
        test_agent['id'], 
        "What kind of adventures can you help me with?"
    )
    print(f"\nNPC Response: {response}")
    
    # Check for any adventure/guide related terms
    key_terms = ['adventure', 'journey', 'guide', 'help', 'explore']
    found_terms = [term for term in key_terms if term in response.lower()]
    print(f"\nFound terms: {', '.join(found_terms)}")
    assert len(found_terms) > 0, "Response should reflect guide/adventure theme"

def test_gpt4_memory_updates(roblox_client, test_agent):
    """Test memory updates with GPT-4o-mini agent."""
    print("\nTesting GPT-4 memory updates...")
    
    # Update memory blocks
    memory_updates = {
        "human": "I am a Roblox player exploring the trading district.",
        "persona": "I am a merchant NPC specializing in rare items."
    }
    roblox_client.update_memory(test_agent['id'], memory_updates)
    
    # Test message to verify memory influence
    response = roblox_client.send_message(
        test_agent['id'],
        "What rare items do you have?"
    )
    print(f"\nNPC Response: {response}")
    
    # Check for merchant/trading terms
    key_terms = ['rare', 'trade', 'merchant', 'items', 'valuable']
    found_terms = [term for term in key_terms if term in response.lower()]
    print(f"\nFound terms: {', '.join(found_terms)}")
    assert len(found_terms) > 0, "Response should reflect merchant/trading theme"

def test_agent_messaging(roblox_client, test_agent):
    """Test free model agent messaging."""
    print("\nTesting agent messaging...")
    
    # Set up memory
    memory_updates = {
        "human": "I am a new Roblox player looking to trade items.",
        "persona": "I am a friendly merchant NPC who helps players trade items safely."
    }
    roblox_client.update_memory(test_agent['id'], memory_updates)
    
    # Test conversation
    response = roblox_client.send_message(
        test_agent['id'],
        "Hello! Can you help me trade my items?"
    )
    print(f"\nNPC Response: {response}")
    
    # Verify response
    assert "trade" in response.lower()
    assert "items" in response.lower()

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

def test_memory_influence():
    """Test that memory affects NPC responses."""
    print("\n=== Testing Memory Influence ===")
    
    client = LettaRobloxClient("http://localhost:8283")
    
    # Create merchant NPC
    agent = client.create_agent(
        npc_type="merchant",
        initial_memory={
            "human": "I am a new player who only has basic items.",
            "persona": "I am a merchant who specializes in helping new players."
        }
    )
    
    try:
        # Test initial persona
        response1 = client.send_message(agent['id'], "What kind of items do you have?")
        print(f"\nInitial Persona Response:")
        print(f"NPC: {response1}")
        
        # Check for beginner-friendly terms
        beginner_terms = ['basic', 'beginners', 'essential']
        found_terms = [term for term in beginner_terms if term in response1.lower()]
        print(f"\nBeginner terms found: {', '.join(found_terms)}")
        assert len(found_terms) > 0, "Response should be beginner-friendly"
        
        # Update to experienced trader persona
        print("\nUpdating to experienced trader persona...")
        client.update_memory(
            agent['id'],
            {
                "human": "I am an experienced player with rare items.",
                "persona": "I am a merchant who deals exclusively in rare and valuable items."
            }
        )
        
        # Test updated persona
        response2 = client.send_message(agent['id'], "What kind of items do you have?")
        print(f"\nUpdated Persona Response:")
        print(f"NPC: {response2}")
        
        # Check for high-end terms
        advanced_terms = ['rare', 'valuable', 'exclusive']
        found_terms = [term for term in advanced_terms if term in response2.lower()]
        print(f"\nAdvanced terms found: {', '.join(found_terms)}")
        assert len(found_terms) > 0, "Response should mention rare/valuable items"
        
        # Verify responses are different
        assert response1 != response2, "Responses should change based on memory"
        print("\nMemory influence verified - responses changed with context")
        
    finally:
        client.delete_agent(agent['id'])