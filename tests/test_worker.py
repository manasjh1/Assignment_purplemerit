from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock, AsyncMock # Ensure AsyncMock is here
import uuid

client = TestClient(app)

def test_job_submission_flow():
    """FIXED: Added missing AsyncMock import."""
    with patch("app.routers.jobs.push_job_to_queue", new_callable=AsyncMock) as mock_queue:
        mock_queue.return_value = True

        # Mock auth to reach the internal logic
        headers = {"Authorization": "Bearer fake-token"}
        with patch("app.core.security.supabase.auth.get_user") as mock_user:
            mock_user.return_value = MagicMock(user=MagicMock(id=uuid.uuid4()))
            
            job_payload = {"task_name": "test_job", "payload": {"key": "value"}}
            response = client.post("/api/v1/jobs/run", json=job_payload, headers=headers)
            
            assert response.status_code == 200
            assert response.json()["status"] == "queued"