"""
FastAPI application setup for newspaper service.
"""

from fastapi import FastAPI

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
async def startup_db_client():
    """Initialize database connection on startup."""
    # MongoDB connection is initialized lazily via singleton pattern
    # Ensure database is accessible
    settings = get_mongodb_settings()
    database = MongoDB.get_database()

    # Create unique compound index on interaction collection
    interaction_collection = database[
        settings.GENERATED_CONTENT_INTERACTION_COLLECTION_NAME
    ]
    try:
        interaction_collection.create_index(
            [("generated_content_id", 1), ("user_id", 1), ("interaction_type", 1)],
            unique=True,
            name="unique_interaction",
        )
    except Exception:
        # Index might already exist, which is fine
        pass
