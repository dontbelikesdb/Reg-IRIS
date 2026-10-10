from typing import Dict, Any, Optional
from app.schemas.search import Citation, SearchResultItem

class CitationFormatter:

    @staticmethod
    def build_citation(doc_name: str, version: str, page_number: int, clause_ref: Optional[str] = None) -> Citation:
        """Constructs an auditable clickable citation object."""
        label = f"{doc_name} ({version}) - Page {page_number}"
        if clause_ref:
            label += f", §{clause_ref}"
        
        return Citation(
            document_name=doc_name,
            version=version,
            page_number=page_number,
            clause_reference=clause_ref,
            citation_label=label
        )

    @classmethod
    def format_hit(cls, raw_data: Dict[str, Any], score: float, highlight_snippet: Optional[str] = None) -> SearchResultItem:
        """Converts raw database hit into the frontend SearchResultItem schema."""
        doc_name = raw_data.get("document_name", "Regulatory Document")
        version = raw_data.get("version", "v1.0")
        page_number = int(raw_data.get("page_number", 1))
        clause_ref = raw_data.get("clause_reference")

        citation = cls.build_citation(doc_name, version, page_number, clause_ref)

        content = raw_data.get("content", "")
        # Use highlighted text if available; otherwise truncate raw content
        matched_snippet = highlight_snippet if highlight_snippet else (content[:250] + "..." if len(content) > 250 else content)

        # Detect conflicting effective dates (Improvement 1: Expose uncertainty)
        applicability_warning = None
        if raw_data.get("has_metadata_conflict"):
            applicability_warning = (
                f"Applicability Warning: Conflicting dates detected for {doc_name}. "
                f"Metadata specifies effective from {raw_data.get('effective_from')}, "
                f"but internal clause text specifies alternative timelines."
            )

        return SearchResultItem(
            chunk_id=raw_data.get("chunk_id", ""),
            doc_id=raw_data.get("doc_id", ""),
            citation=citation,
            parent_header=raw_data.get("parent_header"),
            content=content,
            matched_snippet=matched_snippet,
            regulator=raw_data.get("regulator", "N/A"),
            jurisdiction=raw_data.get("jurisdiction", "N/A"),
            category=raw_data.get("category", "General"),
            effective_from=raw_data.get("effective_from"),
            effective_to=raw_data.get("effective_to"),
            score=round(score, 4),
            applicability_warning=applicability_warning,
            prev_chunk_id=raw_data.get("prev_chunk_id"),
            next_chunk_id=raw_data.get("next_chunk_id")
        )