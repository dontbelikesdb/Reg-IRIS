from app.services.fusion.rrf_ranker import RRFRanker

def test_rrf_fuses_lexical_and_dense_hits():
    lexical_hits = [
        {"_id": "chunk_1", "_source": {"chunk_id": "chunk_1", "document_name": "MiFID II", "page_number": 1, "version": "v2.0", "content": "LEI mandate"}}
    ]
    dense_hits = [
        {"chunk_id": "chunk_1", "metadata": {"document_name": "MiFID II", "page_number": 1, "version": "v2.0"}, "document": "LEI mandate"}
    ]

    fused = RRFRanker.fuse(lexical_hits, dense_hits, top_k=5)
    assert len(fused) == 1
    assert fused[0].chunk_id == "chunk_1"
    # RRF score with rank 0 on both: (1/61) + (1/61) = 0.0328
    assert fused[0].score > 0.03

def test_rrf_deduplication():
    lexical_hits = [
        {"_id": "chunk_A", "_source": {"chunk_id": "chunk_A", "document_name": "EMIR", "page_number": 2, "version": "v1.1", "content": "Clearing rules"}}
    ]
    dense_hits = [
        {"chunk_id": "chunk_B", "metadata": {"document_name": "Dodd-Frank", "page_number": 3, "version": "v1.0"}, "document": "Swap rules"}
    ]

    fused = RRFRanker.fuse(lexical_hits, dense_hits, top_k=5)
    assert len(fused) == 2
    ids = [item.chunk_id for item in fused]
    assert "chunk_A" in ids and "chunk_B" in ids