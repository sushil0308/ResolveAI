"""
main.py
FastAPI application entrypoint for ResolveAI Support Copilot.
Configures CORS, registers API routers, and sets up startup lifecycle.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.api.routes import router as api_router

app = FastAPI(
    title="ResolveAI Support Copilot API",
    description="Enterprise AI Customer Support Copilot grounded in historical Twitter support resolutions",
    version="1.0.0",
)

# Configure CORS: allow all origins by default or specific comma-separated origins from environment
cors_origins_raw = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
allowed_origins = [orig.strip() for orig in cors_origins_raw.split(",") if orig.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(api_router, prefix="/api")

# Determine frontend static distribution directory for unified full-stack serving
frontend_dist_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if not os.path.isdir(frontend_dist_dir):
    frontend_dist_dir = os.path.join("frontend", "dist")

if os.path.isdir(frontend_dist_dir):
    assets_dir = os.path.join(frontend_dist_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        candidate = os.path.join(frontend_dist_dir, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        index_file = os.path.join(frontend_dist_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Page not found")
else:
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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
