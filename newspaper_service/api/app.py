"""
FastAPI application setup for newspaper service.
"""

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
    # Initialize DI injector
    app.state.injector = create_injector()
