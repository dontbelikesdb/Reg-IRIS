import logging
from typing import List, Dict, Any
from app.core.config import settings
from app.schemas.search import SearchRequest, SearchResponse, SearchFacets, FacetBucket, SearchResultItem
from app.services.elastic.es_client import es_client
from app.services.elastic.query_builder import ESQueryBuilder
from app.services.vector.chroma_client import chroma_client
from app.services.vector.embedder import embedder
from app.services.fusion.rrf_ranker import RRFRanker
from app.services.fusion.citation_formatter import CitationFormatter

logger = logging.getLogger(__name__)

class SearchOrchestrator:

    def __init__(self):
        self.es = es_client.get_client()

    def _execute_lexical_search(self, request: SearchRequest) -> Dict[str, Any]:
        """Executes BM25 query against Elasticsearch."""
        body = ESQueryBuilder.build_query(request)
        try:
            return self.es.search(index=settings.ES_INDEX_CLAUSES, body=body)
        except Exception as e:
            logger.error(f"Elasticsearch search failed: {e}")
            return {"hits": {"total": {"value": 0}, "hits": []}}

    def _execute_dense_search(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Encodes query and retrieves nearest vectors from ChromaDB."""
        try:
            query_vector = embedder.embed_query(request.query)
            collection = chroma_client.get_collection()

            # Metadata pre-filtering
            where_filter = {}
            if request.filters and request.filters.regulator:
                where_filter["regulator"] = request.filters.regulator
            if request.filters and request.filters.jurisdiction:
                where_filter["jurisdiction"] = request.filters.jurisdiction

            query_kwargs = {
                "query_embeddings": [query_vector],
                "n_results": min(request.size * 2, 20)
            }
            if where_filter:
                query_kwargs["where"] = where_filter

            raw_res = collection.query(**query_kwargs)

            # Flatten ChromaDB response
            dense_hits = []
            if raw_res and raw_res.get("ids") and len(raw_res["ids"]) > 0:
                ids = raw_res["ids"][0]
                metadatas = raw_res["metadatas"][0] if raw_res.get("metadatas") else [{}] * len(ids)
                documents = raw_res["documents"][0] if raw_res.get("documents") else [""] * len(ids)

                for cid, meta, doc in zip(ids, metadatas, documents):
                    dense_hits.append({
                        "chunk_id": cid,
                        "metadata": meta,
                        "document": doc
                    })
            return dense_hits
        except Exception as e:
            logger.warning(f"ChromaDB search failed (falling back to lexical): {e}")
            return []

    def search(self, request: SearchRequest) -> SearchResponse:
        as_of_date = request.target_date or settings.DEFAULT_REFERENCE_DATE
        mode = request.search_mode.lower()

        lexical_raw = {"hits": {"total": {"value": 0}, "hits": []}}
        dense_hits = []

        if mode in ["hybrid", "keyword"]:
            lexical_raw = self._execute_lexical_search(request)

        if mode in ["hybrid", "semantic"]:
            dense_hits = self._execute_dense_search(request)

        # Determine Fusion Strategy
        es_hits = lexical_raw.get("hits", {}).get("hits", [])
        total_hits = lexical_raw.get("hits", {}).get("total", {}).get("value", 0)

        if mode == "hybrid":
            final_results = RRFRanker.fuse(es_hits, dense_hits, top_k=request.size)
            if not total_hits:
                total_hits = len(final_results)
        elif mode == "keyword":
            final_results = [
                CitationFormatter.format_hit(
                    h["_source"], 
                    h.get("_score", 1.0), 
                    " ... ".join(h.get("highlight", {}).get("content", [])) if h.get("highlight") else None
                ) 
                for h in es_hits
            ]
        else: # semantic
            final_results = [
                CitationFormatter.format_hit(
                    {**d.get("metadata", {}), "content": d.get("document", ""), "chunk_id": d.get("chunk_id")},
                    1.0
                )
                for d in dense_hits[:request.size]
            ]
            total_hits = len(final_results)

        # Extract Facet Counts from ES Aggregations
        facets = None
        if "aggregations" in lexical_raw:
            aggs = lexical_raw["aggregations"]
            facets = SearchFacets(
                regulators=[FacetBucket(key=b["key"], doc_count=b["doc_count"]) for b in aggs.get("regulators", {}).get("buckets", [])],
                jurisdictions=[FacetBucket(key=b["key"], doc_count=b["doc_count"]) for b in aggs.get("jurisdictions", {}).get("buckets", [])],
                categories=[FacetBucket(key=b["key"], doc_count=b["doc_count"]) for b in aggs.get("categories", {}).get("buckets", [])]
            )

        return SearchResponse(
            total_hits=total_hits,
            page=request.page,
            size=request.size,
            search_mode=mode,
            as_of_date_applied=as_of_date,
            results=final_results,
            facets=facets
        )

search_orchestrator = SearchOrchestrator()