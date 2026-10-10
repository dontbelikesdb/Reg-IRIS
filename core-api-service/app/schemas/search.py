from typing import List, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    document_name: str = Field(..., description="e.g. MiFID II RTS 22")
    version: str = Field(..., description="e.g. v2.0")
    page_number: int = Field(..., description="Physical PDF page for clickable citation")
    clause_reference: Optional[str] = Field(None, description="e.g. Article 3, Paragraph 3")
    citation_label: str = Field(..., description="Formatted string: MiFID II RTS 22 (v2.0) - Page 1, §3")

class SearchFilters(BaseModel):
    regulator: Optional[str] = Field(None, description="ESMA, SEC, FCA, CFTC")
    jurisdiction: Optional[str] = Field(None, description="EU, US, UK")
    category: Optional[str] = Field(None, description="Reporting, Clearing, Derivatives")
    version: Optional[str] = Field(None, description="v1.0, v2.0")

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Regulatory search terms or natural language question")
    target_date: Optional[str] = Field(None, description="As-of evaluation date YYYY-MM-DD (Defaults to 2024-07-20)")
    filters: Optional[SearchFilters] = None
    include_superseded: bool = Field(False, description="If False, prunes superseded versions using bitemporal filter")
    search_mode: str = Field("hybrid", description="hybrid | keyword | semantic")
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=50)

class SearchResultItem(BaseModel):
    chunk_id: str
    doc_id: str
    citation: Citation
    parent_header: Optional[str] = None
    content: str
    matched_snippet: str
    regulator: str
    jurisdiction: str
    category: str
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    score: float
    applicability_warning: Optional[str] = None
    prev_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None

class FacetBucket(BaseModel):
    key: str
    doc_count: int

class SearchFacets(BaseModel):
    regulators: List[FacetBucket]
    jurisdictions: List[FacetBucket]
    categories: List[FacetBucket]

class SearchResponse(BaseModel):
    total_hits: int
    page: int
    size: int
    search_mode: str
    as_of_date_applied: str
    results: List[SearchResultItem]
    facets: Optional[SearchFacets] = None