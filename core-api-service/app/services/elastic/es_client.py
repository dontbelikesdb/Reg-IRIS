import logging
from elasticsearch import Elasticsearch
from app.core.config import settings
from app.core.exceptions import ElasticsearchUnavailableError

logger = logging.getLogger(__name__)

class ESClientWrapper:
    _client: Elasticsearch = None

    @classmethod
    def get_client(cls) -> Elasticsearch:
        if cls._client is None:
            try:
                cls._client = Elasticsearch(
                    hosts=[settings.ELASTICSEARCH_URL],
                    request_timeout=15,
                    max_retries=3,
                    retry_on_timeout=True
                )
                if not cls._client.ping():
                    logger.warning(f"Elasticsearch ping failed at {settings.ELASTICSEARCH_URL}")
            except Exception as e:
                logger.error(f"Cannot initialize Elasticsearch client: {e}")
                raise ElasticsearchUnavailableError(f"Elasticsearch connection failed: {str(e)}")
        return cls._client

    @classmethod
    def ping(cls) -> bool:
        try:
            return cls.get_client().ping()
        except Exception:
            return False

es_client = ESClientWrapper()