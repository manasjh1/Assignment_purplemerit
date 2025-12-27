from fastapi import APIRouter, HTTPException
from app.models import UserLogin
from app.services.db import supabase

router = APIRouter()

@router.post("/signup")
def signup(user: UserLogin):
    """
    Creates a new user. 
    Satisfies Requirement: 'Secure authentication'[cite: 23].
    """
    try:
        # Sign up the user via Supabase Auth
        response = supabase.auth.sign_up({
            "email": user.email, 
            "password": user.password
        })
        # Return the unique UUID (id) instead of just the email
        return {
            "message": "Signup successful", 
            "user_id": response.user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

@router.post("/login")
def login(user: UserLogin):
    """
    Authenticates user and returns JWT along with the User ID.
    Satisfies Requirement: 'JWT or OAuth2-based authentication'[cite: 31].
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email, 
            "password": user.password
        })
        
        # Return the session tokens and the unique User ID (UUID)
        return {
            "user_id": response.user.id,
            "access_token": response.session.access_token, 
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")
    
@router.post("/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True)):
    """
    Satisfies Requirement: 'Token refresh mechanism'.[cite_end]
    Takes a refresh token and returns a new access token.
    """
    try:
        # Supabase provides a built-in method to refresh the session
        response = supabase.auth.refresh_session(refresh_token)
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {str(e)}")