from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    owner = "owner"
    collaborator = "collaborator"
    viewer = "viewer"

class UserLogin(BaseModel):
    email: str
    password: str

class ProjectCreate(BaseModel):
    name: str

class ProjectUpdate(BaseModel):
    name: str

class CollaboratorInvite(BaseModel):
    user_id: UUID 
    role: UserRole = UserRole.viewer 

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    task_name: str
    payload: Dict[str, Any]

class JobResponse(BaseModel):
    job_id: str
    status: str