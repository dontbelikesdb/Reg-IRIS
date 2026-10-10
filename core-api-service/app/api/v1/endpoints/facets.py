from fastapi import APIRouter, HTTPException, status
from app.schemas.search import SearchRequest, SearchFacets
from app.services.search_orchestrator import search_orchestrator

router = APIRouter()

@router.get("/", response_model=SearchFacets, status_code=status.HTTP_200_OK, summary="Get Search Filter Facets")
def get_facets():
    """
    Fetches aggregate counts for regulators, jurisdictions, and categories
    to dynamically populate filter dropdowns in the Rest UI.
    """
    try:
        # Request empty query with size=0 to retrieve pure aggregation stats
        dummy_request = SearchRequest(query="*", page=1, size=0, search_mode="keyword")
        res = search_orchestrator.search(dummy_request)
        return res.facets or SearchFacets(regulators=[], jurisdictions=[], categories=[])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch facets: {str(e)}"
        )