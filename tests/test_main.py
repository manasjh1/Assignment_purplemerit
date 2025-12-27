from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Satisfies Requirement: 'Integration tests for APIs' [cite: 91]"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Go to /docs for API documentation"}

def test_auth_validation():
    """Satisfies Requirement: 'Input validation' [cite: 106]"""
    # Try to login with missing password
    response = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 422 # Validation Error