import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.exceptions import ChromaDBUnavailableError

logger = logging.getLogger(__name__)

class ChromaClientWrapper:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                cls._client = chromadb.HttpClient(
                    host=settings.CHROMA_HOST,
                    port=settings.CHROMA_PORT,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
                logger.info(f"Connected to ChromaDB at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
            except Exception as e:
                logger.error(f"ChromaDB connection error: {e}")
                raise ChromaDBUnavailableError(f"Cannot reach ChromaDB: {str(e)}")
        return cls._client

    @classmethod
    def get_collection(cls):
        client = cls.get_client()
        return client.get_or_create_collection(name=settings.CHROMA_COLLECTION)

chroma_client = ChromaClientWrapper()