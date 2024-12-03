import pytest
import os
from letta import LLMConfig, EmbeddingConfig
from dotenv import load_dotenv
from pathlib import Path

# Load root .env file
root_dir = Path(__file__).parent.parent.parent  # Go up to letta-deployment
env_path = root_dir / '.env'
load_dotenv(env_path)

@pytest.fixture
def server_url():
    """Get server URL from environment or use default."""
    return os.getenv('LETTA_SERVER_URL', 'http://localhost:8333')

@pytest.fixture
def docker_url():
    """Get Docker server URL."""
    return os.getenv('LETTA_DOCKER_URL', 'http://localhost:8283')

@pytest.fixture
def free_config():
    """Config for free memgpt.ai endpoints."""
    return {
        "llm": LLMConfig(
            model="letta-free",
            model_endpoint_type="openai",
            model_endpoint="https://inference.memgpt.ai",
            context_window=16384
        ),
        "embedding": EmbeddingConfig(
            embedding_endpoint_type="hugging-face",
            embedding_endpoint="https://embeddings.memgpt.ai",
            embedding_model="letta-free",
            embedding_dim=1024,
            embedding_chunk_size=300
        )
    }

@pytest.fixture
def openai_key():
    """Get OpenAI key from root .env."""
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise ValueError("OPENAI_API_KEY not found in root .env file")
    return key

@pytest.fixture
def openai_config(openai_key):
    """Config for OpenAI endpoints."""
    # Use values from root .env
    return {
        "llm": LLMConfig(
            model=os.getenv('LETTA_LLM_MODEL', 'gpt-4o-mini'),
            model_endpoint_type=os.getenv('LETTA_LLM_ENDPOINT_TYPE', 'openai'),
            model_endpoint=os.getenv('LETTA_LLM_ENDPOINT', 'https://api.openai.com/v1'),
            context_window=int(os.getenv('LETTA_LLM_CONTEXT_WINDOW', '128000'))
        ),
        "embedding": EmbeddingConfig(
            embedding_endpoint_type=os.getenv('LETTA_EMBEDDING_ENDPOINT_TYPE', 'openai'),
            embedding_endpoint=os.getenv('LETTA_EMBEDDING_ENDPOINT', 'https://api.openai.com/v1'),
            embedding_model=os.getenv('LETTA_EMBEDDING_MODEL', 'text-embedding-ada-002'),
            embedding_dim=int(os.getenv('LETTA_EMBEDDING_DIM', '1536')),
            embedding_chunk_size=300
        )
    } 