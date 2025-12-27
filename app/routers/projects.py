from fastapi import APIRouter, HTTPException, Depends, status
from app.models import ProjectCreate, ProjectResponse, ProjectUpdate, CollaboratorInvite
from app.services.db import supabase
from app.core.security import get_current_user
from typing import List
from uuid import UUID

router = APIRouter()

# --- 1. CREATE PROJECT ---
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: ProjectCreate, user = Depends(get_current_user)):
    """Satisfies Requirement: 'Create projects'."""
    data = {"name": project.name, "owner_id": str(user.id)}
    response = supabase.table("projects").insert(data).execute()
    return response.data[0]

# --- 2. GET PROJECTS (READ) ---
@router.get("/", response_model=List[ProjectResponse])
def get_projects(user = Depends(get_current_user)):
    """Fetches projects where user is owner."""
    response = supabase.table("projects").select("*").eq("owner_id", str(user.id)).execute()
    return response.data

# --- 3. UPDATE PROJECT ---
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: UUID, project: ProjectUpdate, user = Depends(get_current_user)):
    """Satisfies Requirement: 'Update projects' with RBAC."""
    # Verify the requester is the owner
    check = supabase.table("projects").select("owner_id").eq("id", str(project_id)).single().execute()
    if not check.data or check.data["owner_id"] != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this project")
    
    response = supabase.table("projects").update({"name": project.name}).eq("id", str(project_id)).execute()
    return response.data[0]

# --- 4. DELETE PROJECT ---
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: UUID, user = Depends(get_current_user)):
    """Satisfies Requirement: 'Delete projects' with RBAC."""
    # Verify ownership before deletion
    check = supabase.table("projects").select("owner_id").eq("id", str(project_id)).single().execute()
    if not check.data or check.data["owner_id"] != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    supabase.table("projects").delete().eq("id", str(project_id)).execute()
    return None

@router.post("/{project_id}/collaborators")
def invite_collaborator(
    project_id: UUID, 
    invite: CollaboratorInvite, 
    user = Depends(get_current_user)
):
    project = supabase.table("projects").select("owner_id").eq("id", str(project_id)).single().execute()
    if not project.data or project.data["owner_id"] != str(user.id):
        raise HTTPException(status_code=403, detail="Only owners can add collaborators")
    
    role_to_send = str(invite.role.value)
    
    data = {
        "project_id": str(project_id),
        "user_id": str(invite.user_id),
        "role": role_to_send
    }
    
    print(f"DEBUG: Attempting to insert role: '{role_to_send}'")
    
    try:
        response = supabase.table("collaborators").insert(data).execute()
        return {"message": "Collaborator added successfully"}
    except Exception as e:
        print(f"Supabase Error: {e}")
        raise HTTPException(status_code=400, detail=f"DB rejected role '{role_to_send}': {str(e)}")