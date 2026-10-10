class SearchServiceException(Exception):
    """Base exception for Search & Retrieval errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ElasticsearchUnavailableError(SearchServiceException):
    """Raised when Elasticsearch is unreachable."""
    pass

class ChromaDBUnavailableError(SearchServiceException):
    """Raised when ChromaDB is unreachable."""
    pass

class EmbeddingModelError(SearchServiceException):
    """Raised when vector embedding generation fails."""
    pass