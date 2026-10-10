from app.services.fusion.citation_formatter import CitationFormatter

def test_citation_formatting_structure():
    raw_hit = {
        "chunk_id": "MIFID2-P01-C03",
        "document_name": "MiFID II RTS 22",
        "version": "v2.0",
        "page_number": 1,
        "clause_reference": "Article 3, Paragraph 3",
        "content": "All trades require LEI."
    }
    item = CitationFormatter.format_hit(raw_hit, score=0.85)

    assert item.citation.citation_label == "MiFID II RTS 22 (v2.0) - Page 1, §Article 3, Paragraph 3"
    assert item.citation.page_number == 1
    assert item.citation.version == "v2.0"

def test_metadata_conflict_warning_flag():
    raw_hit = {
        "chunk_id": "MIFID-V1-P01",
        "document_name": "MiFID II",
        "version": "v1.0",
        "page_number": 1,
        "effective_from": "2023-07-01",
        "has_metadata_conflict": True,
        "content": "Applies from January 2023."
    }
    item = CitationFormatter.format_hit(raw_hit, score=0.5)
    assert item.applicability_warning is not None
    assert "Conflicting dates detected" in item.applicability_warning