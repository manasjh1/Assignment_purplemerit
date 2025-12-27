from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock, AsyncMock
import uuid
import pytest

client = TestClient(app)

# Use valid UUIDs to satisfy Pydantic validation
VALID_USER_ID = str(uuid.uuid4())
VALID_PROJECT_ID = str(uuid.uuid4())
# Use ISO format for datetimes
ISO_DATE = "2023-01-01T12:00:00"

def mock_auth():
    return patch("app.core.security.supabase.auth.get_user", 
                 return_value=MagicMock(user=MagicMock(id=VALID_USER_ID)))

# --- 1. Test GET (Fixed UUID and Date validation) ---
def test_get_projects_db_success():
    """Targets DB fetch logic with valid data formats."""
    with mock_auth(), \
         patch("app.routers.projects.redis_client.get", new_callable=AsyncMock) as mock_redis_get, \
         patch("app.routers.projects.redis_client.setex", new_callable=AsyncMock), \
         patch("app.routers.projects.supabase.table") as mock_table:
        
        mock_redis_get.return_value = None 
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = \
            MagicMock(data=[{
                "id": VALID_PROJECT_ID, 
                "name": "DB Project", 
                "owner_id": VALID_USER_ID, 
                "created_at": ISO_DATE
            }])
        
        response = client.get("/api/v1/projects/", headers={"Authorization": "Bearer token"})
        assert response.status_code == 200

# --- 2. Test POST (Fixed UUID validation) ---
def test_create_project_success():
    """Targets creation logic with valid mock data."""
    with mock_auth(), \
         patch("app.routers.projects.supabase.table") as mock_table, \
         patch("app.routers.projects.redis_client.delete", new_callable=AsyncMock):
        
        mock_table.return_value.insert.return_value.execute.return_value = \
            MagicMock(data=[{
                "id": VALID_PROJECT_ID, 
                "name": "New Proj", 
                "owner_id": VALID_USER_ID, 
                "created_at": ISO_DATE
            }])
        
        response = client.post("/api/v1/projects/", 
                               json={"name": "New Proj"}, 
                               headers={"Authorization": "Bearer token"})
        
        assert response.status_code in [200, 201]

# --- 3. Test DELETE (Fixed 204 status check) ---
def test_delete_project_success():
    with mock_auth(), \
         patch("app.routers.projects.supabase.table") as mock_table, \
         patch("app.routers.projects.redis_client.delete", new_callable=AsyncMock):
        
        mock_query = MagicMock()
        mock_query.execute.return_value = MagicMock(data={"owner_id": VALID_USER_ID})
        mock_table.return_value.select.return_value.eq.return_value.single.return_value = mock_query
        mock_table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()
        
        response = client.delete(f"/api/v1/projects/{VALID_PROJECT_ID}", headers={"Authorization": "Bearer token"})
        assert response.status_code in [200, 204]

# --- 4. Test Workspace Status ---
def test_get_workspace_status_success():
    with mock_auth(), \
         patch("app.routers.projects.supabase.table") as mock_table:
        
        mock_table.return_value.select.return_value.eq.return_value.single.execute.return_value = MagicMock(data={"owner_id": VALID_USER_ID})
        mock_table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(count=5)
        
        response = client.get(f"/api/v1/projects/{VALID_PROJECT_ID}/workspace/status", headers={"Authorization": "Bearer token"})
        assert response.status_code == 200