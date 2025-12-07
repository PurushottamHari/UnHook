"""
Adapter for converting between internal models and MongoDB models for generated content interactions.
"""

from datetime import datetime, timezone
from uuid import UUID

from ....models.generated_content_interaction import (
    GeneratedContentInteraction, InteractionStatus, InteractionType,
    InteractionTypeDetail)
from ..models.generated_content_interaction_db_model import (
    GeneratedContentInteractionDBModel, InteractionTypeDetailDBModel)


class GeneratedContentInteractionAdapter:
    """Adapter for converting between GeneratedContentInteraction and GeneratedContentInteractionDBModel."""

    @staticmethod
    def to_db_model(
        interaction: GeneratedContentInteraction,
    ) -> GeneratedContentInteractionDBModel:
        """Convert internal GeneratedContentInteraction to MongoDB GeneratedContentInteractionDBModel."""
        return GeneratedContentInteractionDBModel(
            id=str(interaction.id),
            generated_content_id=interaction.generated_content_id,
            user_id=interaction.user_id,
            interaction_type=interaction.interaction_type.value,
            metadata=interaction.metadata,
            created_at=GeneratedContentInteractionAdapter._datetime_to_float(
                interaction.created_at
            ),
            updated_at=GeneratedContentInteractionAdapter._datetime_to_float(
                interaction.updated_at
            ),
            status=interaction.status.value,
            type_details=[
                GeneratedContentInteractionAdapter._type_detail_to_db_model(detail)
                for detail in interaction.type_details
            ],
        )

    @staticmethod
    def to_internal_model(
        db_model: GeneratedContentInteractionDBModel,
    ) -> GeneratedContentInteraction:
        """Convert MongoDB GeneratedContentInteractionDBModel to internal GeneratedContentInteraction."""
        return GeneratedContentInteraction(
            id=UUID(db_model.id),
            generated_content_id=db_model.generated_content_id,
            user_id=db_model.user_id,
            interaction_type=InteractionType(db_model.interaction_type),
            metadata=db_model.metadata,
            created_at=GeneratedContentInteractionAdapter._float_to_datetime(
                db_model.created_at
            ),
            updated_at=GeneratedContentInteractionAdapter._float_to_datetime(
                db_model.updated_at
            ),
            status=InteractionStatus(db_model.status),
            type_details=[
                GeneratedContentInteractionAdapter._type_detail_to_internal_model(detail)
                for detail in db_model.type_details
            ],
        )

    @staticmethod
    def _datetime_to_float(dt: datetime) -> float:
        """Convert datetime to UTC epoch seconds."""
        return dt.astimezone(timezone.utc).timestamp()

    @staticmethod
    def _float_to_datetime(ts: float) -> datetime:
        """Convert UTC epoch seconds to datetime."""
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    @staticmethod
    def _type_detail_to_db_model(detail: InteractionTypeDetail) -> InteractionTypeDetailDBModel:
        """Convert InteractionTypeDetail to InteractionTypeDetailDBModel."""
        return InteractionTypeDetailDBModel(
            interaction_type=detail.interaction_type.value,
            created_at=GeneratedContentInteractionAdapter._datetime_to_float(
                detail.created_at
            ),
            reason=detail.reason,
        )

    @staticmethod
    def _type_detail_to_internal_model(
        db_detail: InteractionTypeDetailDBModel,
    ) -> InteractionTypeDetail:
        """Convert InteractionTypeDetailDBModel to InteractionTypeDetail."""
        return InteractionTypeDetail(
            interaction_type=InteractionType(db_detail.interaction_type),
            created_at=GeneratedContentInteractionAdapter._float_to_datetime(
                db_detail.created_at
            ),
            reason=db_detail.reason,
        )

