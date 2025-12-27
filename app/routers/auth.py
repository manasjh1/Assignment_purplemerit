from fastapi import APIRouter, HTTPException, Body, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models import UserLogin
from app.services.db import supabase

# Initialize local limiter reference for rate limiting
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

@router.post("/signup")
def signup(user: UserLogin):
    """
    Creates a new user in Supabase. 
    Satisfies Requirement: 'Secure authentication'[cite: 186].
    """
    try:
        response = supabase.auth.sign_up({
            "email": user.email, 
            "password": user.password
        })
        return {
            "message": "Signup successful", 
            "user_id": response.user.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

@router.post("/login")
@limiter.limit("5/minute") # Prevents brute-force attacks [cite: 202]
def login(request: Request, user: UserLogin): 
    """
    Authenticates user and returns JWT tokens. 
    Rate limited to 5 attempts per minute[cite: 202].
    Satisfies Requirement: 'JWT or OAuth2-based authentication'[cite: 194].
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email, 
            "password": user.password
        })
        
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
    Exchanges a refresh token for a new access token.
    Satisfies Requirement: 'Token refresh mechanism'.
    """
    try:
        # Supabase requires the refresh_token string to generate a new session
        response = supabase.auth.refresh_session(refresh_token)
        
        # Ensure the response contains a valid new session
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        # If Supabase rejects the token (401), this detail will appear in your logs
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {str(e)}")