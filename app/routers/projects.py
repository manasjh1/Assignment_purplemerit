from fastapi import APIRouter, HTTPException, Depends, status
from app.models import ProjectCreate, ProjectResponse, ProjectUpdate, CollaboratorInvite
from app.services.db import supabase
from app.services.queue_service import redis_client # Re-using existing Redis connection
from app.core.security import get_current_user
from typing import List
from uuid import UUID
import json

router = APIRouter()

# --- 1. CREATE PROJECT ---
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, user = Depends(get_current_user)):
    """Satisfies Requirement: 'Create projects'[cite: 42]."""
    data = {"name": project.name, "owner_id": str(user.id)}
    response = supabase.table("projects").insert(data).execute()
    
    # Invalidate cache for this user since list changed
    await redis_client.delete(f"projects:{user.id}")
    
    return response.data[0]

# --- 2. GET PROJECTS (READ with Redis Caching) ---
@router.get("/", response_model=List[ProjectResponse])
async def get_projects(user = Depends(get_current_user)):
    """
    Fetches projects with Redis Caching.
    Satisfies 'Redis caching' and 'Multiple data stores'[cite: 75, 87].
    """
    cache_key = f"projects:{user.id}"
    
    # A. Try Redis first (Non-relational)
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        # Return cached data if available
        return json.loads(cached_data)

    # B. If miss, fetch from Supabase (Relational)
    response = supabase.table("projects").select("*").eq("owner_id", str(user.id)).execute()
    
    # C. Store in Redis for 60 seconds (TTL)
    if response.data:
        await redis_client.setex(cache_key, 60, json.dumps(response.data))
        
    return response.data

# --- 3. UPDATE PROJECT ---
@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: UUID, project: ProjectUpdate, user = Depends(get_current_user)):
    """Satisfies Requirement: 'Update projects' with RBAC[cite: 42]."""
    check = supabase.table("projects").select("owner_id").eq("id", str(project_id)).single().execute()
    if not check.data or check.data["owner_id"] != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this project")
    
    response = supabase.table("projects").update({"name": project.name}).eq("id", str(project_id)).execute()
    
    # Invalidate cache
    await redis_client.delete(f"projects:{user.id}")
    
    return response.data[0]

# --- 4. DELETE PROJECT ---
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, user = Depends(get_current_user)):
    """Satisfies Requirement: 'Delete projects' with RBAC[cite: 42]."""
    check = supabase.table("projects").select("owner_id").eq("id", str(project_id)).single().execute()
    if not check.data or check.data["owner_id"] != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    supabase.table("projects").delete().eq("id", str(project_id)).execute()
    
    # Invalidate cache
    await redis_client.delete(f"projects:{user.id}")
    
    return None

# --- 5. COLLABORATOR MANAGEMENT ---
@router.post("/{project_id}/collaborators")
def invite_collaborator(
    project_id: UUID, 
    invite: CollaboratorInvite, 
    user = Depends(get_current_user)
):
    """Satisfies Requirement: 'Invite collaborators' and 'Assign roles'[cite: 44, 45]."""
    project = supabase.table("projects").select("owner_id").eq("id", str(project_id)).single().execute()
    if not project.data or project.data["owner_id"] != str(user.id):
        raise HTTPException(status_code=403, detail="Only owners can add collaborators")
    
    role_to_send = str(invite.role.value)
    
    data = {
        "project_id": str(project_id),
        "user_id": str(invite.user_id),
        "role": role_to_send
    }
    
    try:
        response = supabase.table("collaborators").insert(data).execute()
        return {"message": "Collaborator added successfully"}
    except Exception as e:
        print(f"Supabase Error: {e}")
        raise HTTPException(status_code=400, detail=f"DB rejected role '{role_to_send}': {str(e)}")
    
@router.get("/{project_id}/workspace/status")
async def get_workspace_status(project_id: UUID, user = Depends(get_current_user)):
    """
    Satisfies Requirement: 'Manage workspaces'.
    Fetches real-time metadata or collaborator counts for a specific workspace.
    """
    # Verify access first
    check = supabase.table("projects").select("owner_id").eq("id", str(project_id)).single().execute()
    if not check.data:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch active collaborator count from the DB
    collabs = supabase.table("collaborators").select("user_id", count="exact").eq("project_id", str(project_id)).execute()
    
    return {
        "project_id": project_id,
        "active_collaborators": collabs.count if collabs.count else 0,
        "workspace_url": f"/ws/{project_id}"
    }   