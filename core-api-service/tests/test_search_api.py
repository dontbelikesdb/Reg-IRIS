from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_search_endpoint_contract():
    payload = {
        "query": "LEI reporting requirements",
        "search_mode": "keyword",
        "page": 1,
        "size": 5
    }
    response = client.post("/api/v1/search/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_hits" in data
    assert "results" in data
    assert "as_of_date_applied" in data

def test_chat_endpoint_contract():
    payload = {
        "question": "What is the reporting deadline for swaps?"
    }
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "grounded_sources" in data
    assert isinstance(data["grounded_sources"], list)