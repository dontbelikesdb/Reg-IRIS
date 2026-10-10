from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

index_name = "regulatory_clauses"

mapping = {
    "mappings": {
        "properties": {
            "content": {"type": "text"},
            "page_number": {"type": "integer"},
            "regulator": {"type": "keyword"},
            "jurisdiction": {"type": "keyword"},
            "effective_date": {"type": "date"}
        }
    }
}

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)
    print(f"Index {index_name} created.")
else:
    print(f"Index {index_name} already exists.")