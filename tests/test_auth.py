from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
import pytest

client = TestClient(app)

def test_signup_success():
    with patch("app.routers.auth.supabase.auth.sign_up") as mock_signup:
        mock_signup.return_value = MagicMock(user=MagicMock(id="test-uuid"))
        response = client.post("/api/v1/auth/signup", json={"email": "test@test.com", "password": "password"})
        assert response.status_code == 200

def test_login_success():
    with patch("app.routers.auth.supabase.auth.sign_in_with_password") as mock_login:
        mock_login.return_value = MagicMock(
            user=MagicMock(id="user-123"),
            session=MagicMock(access_token="abc", refresh_token="def")
        )
        response = client.post("/api/v1/auth/login", json={"email": "test@test.com", "password": "password"})
        assert response.status_code == 200

def test_refresh_token_success():
    """Targets the refresh logic to increase auth.py coverage."""
    with patch("app.routers.auth.supabase.auth.refresh_session") as mock_refresh:
        mock_refresh.return_value = MagicMock(
            session=MagicMock(access_token="new_abc", refresh_token="new_def")
        )
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "valid_token"})
        assert response.status_code == 200
        assert response.json()["access_token"] == "new_abc"

def test_refresh_token_failure():
    """Targets the 'except' block in auth.py."""
    with patch("app.routers.auth.supabase.auth.refresh_session", side_effect=Exception("Invalid")):
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "bad_token"})
        assert response.status_code == 401