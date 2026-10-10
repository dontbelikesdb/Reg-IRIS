from fastapi import APIRouter, HTTPException, status
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_orchestrator import search_orchestrator

router = APIRouter()

@router.post("/", response_model=SearchResponse, status_code=status.HTTP_200_OK, summary="Hybrid Regulatory Clause Search")
def search_clauses(payload: SearchRequest):
    """
    Search regulatory clauses across Elasticsearch (BM25) and ChromaDB (Dense Vectors).
    - Returns exact matching paragraphs with clickable citations (Document Name + Page).
    - Enforces deterministic bitemporal date validity.
    - Fuses results using Reciprocal Rank Fusion (RRF).
    """
    try:
        return search_orchestrator.search(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search service error: {str(e)}"
        )