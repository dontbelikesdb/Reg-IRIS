import logging
from typing import List
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.exceptions import EmbeddingModelError

logger = logging.getLogger(__name__)

class LocalEmbedder:
    _model: SentenceTransformer = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            logger.info(f"Loading local embedding model: {settings.EMBEDDING_MODEL_NAME}")
            try:
                cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model: {e}")
                raise EmbeddingModelError(f"Embedding model initialization failed: {str(e)}")
        return cls._model

    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        """Encodes query text into a 384-dimensional dense vector."""
        model = cls.get_model()
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()

embedder = LocalEmbedder()