import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "vector_store_chunks" in data
    assert "total_properties_stored" in data


def test_sources_endpoint():
    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    data = response.json()
    assert "platforms" in data
    assert len(data["platforms"]) == 2
    assert data["total_records"] > 0


def test_projects_endpoint():
    response = client.get("/api/v1/projects?page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert len(data["projects"]) > 0
    first = data["projects"][0]
    assert "project_name" in first
    assert "source_url" in first


def test_projects_filter_source():
    response = client.get("/api/v1/projects?source=DarGlobal&page_size=5")
    assert response.status_code == 200
    data = response.json()
    for p in data["projects"]:
        assert p["source"] == "DarGlobal"


def test_admin_ingest_protection():
    # Without admin secret
    response = client.post("/api/v1/admin/ingest")
    assert response.status_code == 403

    # With invalid admin secret
    response = client.post("/api/v1/admin/ingest", headers={"X-Admin-Secret": "wrong"})
    assert response.status_code == 403
