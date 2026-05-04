"""
FastAPI application setup for newspaper service.
"""

import os

from fastapi import FastAPI

from ..infra.dependency_injection.registration import create_injector
from ..repositories.mongodb.config.database import MongoDB
from ..repositories.mongodb.config.settings import get_mongodb_settings
from .controllers.generated_content_controller import \
    router as interaction_router
from .controllers.newspaper_controller import router as newspaper_router

app = FastAPI(
    title="Newspaper Service API",
    description="API for managing newspapers and content interactions",
    version="1.0.0",
)

# Include routers
app.include_router(interaction_router)
app.include_router(newspaper_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "service": "newspaper-service"}


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    print("PORT FROM ENV:", os.environ.get("PORT"))
    # Initialize DI injector
    app.state.injector = create_injector()


if __name__ == "__main__":
    import uvicorn

    from newspaper_service.config.config import Config

    config = Config()
    port = config.service_port
    print(f"Starting Newspaper Service API on port {port}")
    uvicorn.run(
        "newspaper_service.api.app:app", host="0.0.0.0", port=port, reload=False
    )
