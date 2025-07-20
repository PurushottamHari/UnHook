from datetime import datetime

from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus, GeneratedData, StatusDetail)
from user_service.models.enums import OutputType

from ..models.output import CompleteContentOutput


class CompleteContentOutputAdaptor:
    @staticmethod
    def to_dict(output: CompleteContentOutput) -> dict:
        return {
            "article_markdown": output.article_markdown,
        }

    @staticmethod
    def to_generated_data(output: CompleteContentOutput) -> GeneratedData:
        return GeneratedData(
            string=output.article_markdown, markdown_string=output.article_markdown
        )

    @staticmethod
    def update_generated_content(
        content: GeneratedContent,
        output: CompleteContentOutput,
        output_type: OutputType,
    ) -> GeneratedContent:
        # Only update the generated, status, status_details, and updated_at fields
        content.generated[output_type] = CompleteContentOutputAdaptor.to_generated_data(
            output
        )
        # Optionally, update status and append a new status detail if needed
        # Example: content.set_status(GeneratedContentStatus.CATEGORIZATION_COMPLETED, "Content updated.")
        return content
