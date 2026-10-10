from fastapi import APIRouter
from app.api.v1.endpoints import search, facets, chat

api_router = APIRouter()

api_router.include_router(search.router, prefix="/search", tags=["Regulatory Search"])
api_router.include_router(facets.router, prefix="/search/facets", tags=["Filter Facets"])
api_router.include_router(chat.router, prefix="/chat", tags=["Compliance Q&A Chat"])