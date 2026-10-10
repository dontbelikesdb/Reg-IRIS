from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class GroundedSource(BaseModel):
    citation_label: str
    document_name: str
    version: str
    page_number: int
    clause_reference: Optional[str] = None
    excerpt: str

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural language compliance query")
    target_date: Optional[str] = Field(None, description="As-of evaluation date YYYY-MM-DD")
    regulator_hint: Optional[str] = Field(None, description="Optional regulator bias (ESMA, SEC, FCA, CFTC)")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=[], description="Previous user/assistant turns")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Synthesized response with inline citations [DOC, p. X]")
    grounded_sources: List[GroundedSource] = Field(..., description="Clickable source passages")
    confidence_score: float
    has_applicability_warning: bool
    warning_details: Optional[str] = None