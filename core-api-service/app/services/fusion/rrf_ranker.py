from typing import List, Dict, Any
from app.core.config import settings
from app.schemas.search import SearchResultItem
from app.services.fusion.citation_formatter import CitationFormatter

class RRFRanker:

    @staticmethod
    def fuse(
        lexical_hits: List[Dict[str, Any]], 
        dense_hits: List[Dict[str, Any]], 
        top_k: int = 10
    ) -> List[SearchResultItem]:
        """
        Combines Elasticsearch BM25 hits and ChromaDB vector hits using RRF.
        Handles deduplication and normalizes different score ranges.
        """
        k = settings.RRF_K
        w_lexical = settings.WEIGHT_LEXICAL
        w_dense = settings.WEIGHT_DENSE

        scores: Dict[str, float] = {}
        data_lookup: Dict[str, Dict[str, Any]] = {}
        highlights: Dict[str, str] = {}

        # 1. Process Lexical Hits (Elasticsearch)
        for rank, hit in enumerate(lexical_hits):
            src = hit["_source"]
            chunk_id = src.get("chunk_id") or hit["_id"]
            
            data_lookup[chunk_id] = src
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (w_lexical / (k + rank + 1))

            # Capture ES highlight marks
            hl = hit.get("highlight", {}).get("content", [])
            if hl:
                highlights[chunk_id] = " ... ".join(hl)

        # 2. Process Dense Hits (ChromaDB)
        for rank, hit in enumerate(dense_hits):
            chunk_id = hit.get("chunk_id")
            if not chunk_id:
                continue

            if chunk_id not in data_lookup:
                data_lookup[chunk_id] = hit.get("metadata", {})
                data_lookup[chunk_id]["content"] = hit.get("document", "")
                data_lookup[chunk_id]["chunk_id"] = chunk_id

            scores[chunk_id] = scores.get(chunk_id, 0.0) + (w_dense / (k + rank + 1))

        # 3. Sort by fused score descending
        ranked_chunk_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        # 4. Assemble final SearchResultItem objects
        fused_results: List[SearchResultItem] = []
        for cid in ranked_chunk_ids[:top_k]:
            raw_data = data_lookup[cid]
            hl_snippet = highlights.get(cid)
            fused_score = scores[cid]

            fused_results.append(
                CitationFormatter.format_hit(raw_data, fused_score, hl_snippet)
            )

        return fused_results