from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth, projects, realtime, jobs

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs", # Swagger UI
    openapi_url="/api/v1/openapi.json" # Versioned schema
)

# Satisfies Requirement: 'API versioning strategy'.[cite_end]
# We group all routers under /api/v1
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(realtime.router, tags=["Realtime"]) # WebSocket usually stays at root or /ws

@app.get("/")
def root():
    return {"message": "Go to /docs for API documentation"}