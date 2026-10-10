from typing import Dict, Any, List
from app.core.config import settings
from app.schemas.search import SearchRequest

class ESQueryBuilder:

    @staticmethod
    def build_query(request: SearchRequest) -> Dict[str, Any]:
        as_of_date = request.target_date or settings.DEFAULT_REFERENCE_DATE
        from_offset = (request.page - 1) * request.size

        # 1. Multi-match lexical search with weighted boosts
        must_clauses: List[Dict[str, Any]] = [
            {
                "multi_match": {
                    "query": request.query,
                    "fields": [
                        "content^3.0",
                        "parent_header^2.0",
                        "document_name^1.5",
                        "clause_reference^1.5"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                    "prefix_length": 2
                }
            }
        ]

        filter_clauses: List[Dict[str, Any]] = []

        # 2. Deterministic Bitemporal Validity Filter
        # Include documents that were in force as of target_date
        if not request.include_superseded:
            filter_clauses.append({
                "range": {
                    "effective_from": {
                        "lte": as_of_date
                    }
                }
            })
            filter_clauses.append({
                "bool": {
                    "should": [
                        {"bool": {"must_not": {"exists": {"field": "effective_to"}}}},
                        {"range": {"effective_to": {"gt": as_of_date}}}
                    ],
                    "minimum_should_match": 1
                }
            })

        # 3. Explicit / Tentative Metadata Filters
        if request.filters:
            if request.filters.regulator:
                filter_clauses.append({"term": {"regulator": request.filters.regulator}})
            if request.filters.jurisdiction:
                filter_clauses.append({"term": {"jurisdiction": request.filters.jurisdiction}})
            if request.filters.category:
                filter_clauses.append({"term": {"category": request.filters.category}})
            if request.filters.version:
                filter_clauses.append({"term": {"version": request.filters.version}})

        # 4. Assemble Elasticsearch Request Body
        body: Dict[str, Any] = {
            "from": from_offset,
            "size": request.size,
            "query": {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
                }
            },
            # Exact keyword highlighting for Rest UI
            "highlight": {
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
                "fields": {
                    "content": {
                        "fragment_size": 250,
                        "number_of_fragments": 2
                    }
                }
            },
            # Facets for search sidebar filters
            "aggs": {
                "regulators": {"terms": {"field": "regulator", "size": 10}},
                "jurisdictions": {"terms": {"field": "jurisdiction", "size": 10}},
                "categories": {"terms": {"field": "category", "size": 10}}
            }
        }

        return body