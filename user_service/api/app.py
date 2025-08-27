"""
FastAPI application setup.
"""

from controllers.user_controller import router as user_router
from fastapi import FastAPI
from repositories.mongodb import MongoDB

app = FastAPI(
    title="User Service API", description="API for managing user data", version="1.0.0"
)

# Include routers
app.include_router(user_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "service": "user-service"}


@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup."""
    await MongoDB.connect_to_database()
    collection = MongoDB.get_database()["users"]
    # Create a unique index on the email field
    await collection.create_index("email", unique=True)


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown."""
    await MongoDB.close_database_connection()
