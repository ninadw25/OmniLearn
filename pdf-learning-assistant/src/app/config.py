import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    # API Keys
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    ASTRADB_API_KEY = os.getenv("ASTRADB_API_KEY")
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL")
    CONSISTENCY_LEVEL = "LOCAL_QUORUM"  # Example consistency level for Cassandra
    
    # Other settings
    EMBEDDING_MODEL = "your_embedding_model_name"  # Specify your embedding model name
    VECTOR_STORE_TABLE = "your_vector_store_table_name"  # Specify your vector store table name