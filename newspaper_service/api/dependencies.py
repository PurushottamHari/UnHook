"""
Dependency injection setup for the API.
"""

from fastapi import Depends, Header, HTTPException
from typing_extensions import Annotated

from ..external.user_service import UserServiceClient
from ..repositories.generated_content_interaction_repository import \
    GeneratedContentInteractionRepository
from ..repositories.generated_content_repository import \
    GeneratedContentRepository
from ..repositories.mongodb.generated_content_interaction_repository import \
    MongoDBGeneratedContentInteractionRepository
from ..repositories.mongodb.generated_content_repository import \
    MongoDBGeneratedContentRepository
from ..repositories.mongodb.newspaper_repository import \
    MongoDBNewspaperRepository
from ..repositories.mongodb.user_collected_content_repository import \
    MongoDBUserCollectedContentRepository
from ..repositories.newspaper_repository import NewspaperRepository
from ..repositories.user_collected_content_repository import \
    UserCollectedContentRepository
from ..services.generated_content_interaction_service import \
    ContentInteractionService
from ..services.generated_content_service import GeneratedContentService
from ..services.newspaper_service import NewspaperService
from ..services.validations.validate_create_article_interaction_request_service import \
    ValidateCreateArticleInteractionRequestService


async def get_generated_content_interaction_repository() -> (
    MongoDBGeneratedContentInteractionRepository
):
    """Get MongoDB generated content interaction repository instance."""
    return MongoDBGeneratedContentInteractionRepository()


async def get_validate_create_article_interaction_request_service(
    repository: GeneratedContentInteractionRepository = Depends(
        get_generated_content_interaction_repository
    ),
) -> ValidateCreateArticleInteractionRequestService:
    """Get validation service instance with repository dependency."""
    return ValidateCreateArticleInteractionRequestService(repository)


async def get_user_service_client() -> UserServiceClient:
    """Get user service client instance."""
    return UserServiceClient()


async def get_generated_content_repository() -> MongoDBGeneratedContentRepository:
    """Get MongoDB generated content repository instance."""
    return MongoDBGeneratedContentRepository()


async def get_generated_content_interaction_service(
    repository: GeneratedContentInteractionRepository = Depends(
        get_generated_content_interaction_repository
    ),
    validation_service: ValidateCreateArticleInteractionRequestService = Depends(
        get_validate_create_article_interaction_request_service
    ),
    user_service_client: UserServiceClient = Depends(get_user_service_client),
    generated_content_repository: GeneratedContentRepository = Depends(
        get_generated_content_repository
    ),
) -> ContentInteractionService:
    """Get content interaction service instance with all required dependencies."""
    return ContentInteractionService(
        repository,
        validation_service,
        user_service_client,
        generated_content_repository,
    )


async def get_user_collected_content_repository() -> (
    MongoDBUserCollectedContentRepository
):
    """Get MongoDB user collected content repository instance."""
    return MongoDBUserCollectedContentRepository()


async def get_newspaper_repository(
    user_collected_content_repository: UserCollectedContentRepository = Depends(
        get_user_collected_content_repository
    ),
) -> MongoDBNewspaperRepository:
    """Get MongoDB newspaper repository instance with user collected content repository dependency."""
    return MongoDBNewspaperRepository(user_collected_content_repository)


async def get_generated_content_service(
    generated_content_repository: GeneratedContentRepository = Depends(
        get_generated_content_repository
    ),
    newspaper_repository: NewspaperRepository = Depends(get_newspaper_repository),
    user_collected_content_repository: UserCollectedContentRepository = Depends(
        get_user_collected_content_repository
    ),
    interaction_repository: GeneratedContentInteractionRepository = Depends(
        get_generated_content_interaction_repository
    ),
    user_service_client: UserServiceClient = Depends(get_user_service_client),
) -> GeneratedContentService:
    """Get generated content service instance with all required dependencies."""
    return GeneratedContentService(
        generated_content_repository,
        newspaper_repository,
        user_collected_content_repository,
        interaction_repository,
        user_service_client,
    )


async def get_newspaper_service(
    newspaper_repository: NewspaperRepository = Depends(get_newspaper_repository),
    user_service_client: UserServiceClient = Depends(get_user_service_client),
) -> NewspaperService:
    """Get newspaper service instance with repository and user service client dependencies."""
    return NewspaperService(newspaper_repository, user_service_client)


async def get_user_id_from_header(
    user_id: Annotated[
        str, Header(alias="X-User-ID", description="User ID from header")
    ],
) -> str:
    """
    Extract user_id from X-User-ID header.

    Args:
        user_id: User ID from X-User-ID header

    Returns:
        User ID string

    Raises:
        HTTPException: If user_id header is missing
    """
    if not user_id:
        raise HTTPException(
            status_code=401, detail="User ID header (X-User-ID) is required"
        )
    return user_id
