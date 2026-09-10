"""
main.py
FastAPI application entrypoint for ResolveAI Support Copilot.
Configures CORS, registers API routers, and sets up startup lifecycle.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router as api_router

app = FastAPI(
    title="ResolveAI Support Copilot API",
    description="Enterprise AI Customer Support Copilot grounded in historical Twitter support resolutions",
    version="1.0.0",
)

# Enable CORS for frontend local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ResolveAI Support Copilot API",
        "docs_url": "/docs",
        "health_url": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
