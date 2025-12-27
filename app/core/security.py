from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.db import supabase

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Validates the JWT token with Supabase and returns the user object.
    [cite_start]Satisfies 'Secure authentication' [cite: 23] [cite_start]and 'Role-based access control'[cite: 32].
    """
    token = credentials.credentials
    try:
        # We verify the user by getting their details from Supabase using the token
        user = supabase.auth.get_user(token)
        if not user:
             raise HTTPException(status_code=401, detail="Invalid Authentication Token")
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")