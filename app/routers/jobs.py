from fastapi import APIRouter, Depends
import uuid
from app.models import JobCreate, JobResponse
from app.services.queue_service import push_job_to_queue
from app.core.security import get_current_user

router = APIRouter()

@router.post("/run", response_model=JobResponse)
async def run_job(job: JobCreate, user = Depends(get_current_user)):
    job_id = str(uuid.uuid4())
    job_data = {
        "id": job_id,
        "user_id": str(user.id),
        "task_name": job.task_name,
        "payload": job.payload
    }
    # Push to Redis for processing [cite: 67]
    await push_job_to_queue(job_data)
    return {"job_id": job_id, "status": "queued"}