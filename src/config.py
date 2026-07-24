"""
config.py - Configuration management for DocuMind.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database and FAISS paths
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "data/documind.db")
FAISS_INDEX_PATH = BASE_DIR / os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
FAISS_INDEX_PATH.mkdir(parents=True, exist_ok=True)

# Example Documents Path
EXAMPLE_DOCS_DIR = DATA_DIR / "example_docs"
EXAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_CHAT_MODEL = os.getenv("DEFAULT_CHAT_MODEL", "llama3")
DEFAULT_EMBED_MODEL = os.getenv("DEFAULT_EMBED_MODEL", "nomic-embed-text")

# Document processing settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
