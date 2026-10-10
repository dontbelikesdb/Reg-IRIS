import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Reg IRIS - Search & Retrieval Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Elasticsearch
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    ES_INDEX_CLAUSES: str = "regulatory_clauses"

    # ChromaDB (Vector Store)
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", 8002))
    CHROMA_COLLECTION: str = "regulatory_embeddings"

    # Local CPU Embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # System Reference Date (Matches latest corpus upload: 2024-07-20)
    DEFAULT_REFERENCE_DATE: str = "2024-07-20"

    # Hybrid Search Weights
    RRF_K: int = 60
    WEIGHT_LEXICAL: float = 1.0
    WEIGHT_DENSE: float = 1.0

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()