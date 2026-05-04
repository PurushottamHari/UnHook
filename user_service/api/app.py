"""
FastAPI application setup.
"""

import os

import uvicorn
from fastapi import FastAPI

from user_service.config.config import Config

from ..controllers.user_controller import router as user_router
from ..repositories.mongodb import MongoDB

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
    print("PORT FROM ENV:", os.environ.get("PORT"))
    await MongoDB.connect_to_database()
    collection = MongoDB.get_database()["users"]
    # Create a unique index on the email field
    await collection.create_index("email", unique=True)


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown."""
    await MongoDB.close_database_connection()


if __name__ == "__main__":
    config = Config()
    port = config.service_port
    print(f"Starting User Service API on port {port}")
    uvicorn.run("user_service.api.app:app", host="0.0.0.0", port=port, reload=False)
