from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Project Settings
    PROJECT_NAME: str = "Purple Merit Collaborative Workspace"
    
    # Supabase Configuration
    # These match the SUPABASE_URL and SUPABASE_KEY in your .env
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Redis Cloud Configuration
    # These match the individual REDIS fields in your .env
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str = "default"
    REDIS_PASSWORD: str

    class Config:
        # This tells Pydantic to look for the .env file in the root directory
        env_file = ".env"
        case_sensitive = True

# Initialize the settings object to be used across the app
settings = Settings()