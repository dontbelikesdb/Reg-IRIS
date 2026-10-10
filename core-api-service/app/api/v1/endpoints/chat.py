from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat.rag_engine import rag_engine

router = APIRouter()

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK, summary="Grounded Compliance Q&A Chat")
def answer_regulatory_chat(payload: ChatRequest):
    """
    Answers natural language compliance questions using grounded RAG.
    - Strictly cites source document name, version, and page number.
    - Prevents hallucinations by bounding context to retrieved clauses.
    """
    try:
        return rag_engine.generate_grounded_answer(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat generation failed: {str(e)}"
        )