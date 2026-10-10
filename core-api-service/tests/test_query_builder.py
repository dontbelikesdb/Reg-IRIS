from app.schemas.search import SearchRequest, SearchFilters
from app.services.elastic.query_builder import ESQueryBuilder

def test_query_builder_multi_match_fields():
    req = SearchRequest(query="LEI GLEIF requirement")
    query_body = ESQueryBuilder.build_query(req)
    
    must_block = query_body["query"]["bool"]["must"][0]["multi_match"]
    assert "content^3.0" in must_block["fields"]
    assert "parent_header^2.0" in must_block["fields"]
    assert must_block["query"] == "LEI GLEIF requirement"

def test_query_builder_bitemporal_filter_applied():
    req = SearchRequest(query="margin rules", target_date="2023-05-15", include_superseded=False)
    query_body = ESQueryBuilder.build_query(req)
    
    filters = query_body["query"]["bool"]["filter"]
    # Check effective_from <= 2023-05-15 is present
    range_filter = [f for f in filters if "range" in f and "effective_from" in f["range"]][0]
    assert range_filter["range"]["effective_from"]["lte"] == "2023-05-15"

def test_query_builder_tentative_regulator_filter():
    filters = SearchFilters(regulator="ESMA", jurisdiction="EU")
    req = SearchRequest(query="derivative clearing", filters=filters)
    query_body = ESQueryBuilder.build_query(req)
    
    terms = [f["term"] for f in query_body["query"]["bool"]["filter"] if "term" in f]
    assert {"regulator": "ESMA"} in terms
    assert {"jurisdiction": "EU"} in terms