from datetime import datetime

from data_processing_service.models.generated_content import (
    GeneratedContent,
    GeneratedContentStatus,
    GeneratedData,
    StatusDetail,
)
from user_service.models.enums import OutputType


class CompleteContentOutputAdaptor:
    @staticmethod
    def to_dict(output: str) -> dict:
        return {
            "article_markdown": output,
        }

    @staticmethod
    def to_generated_data(output: str) -> GeneratedData:
        return GeneratedData(string=output, markdown_string=output)

    @staticmethod
    def update_generated_content(
        content: GeneratedContent,
        output: str,
        output_type: OutputType,
    ) -> GeneratedContent:
        # Only update the generated, status, status_details, and updated_at fields
        content.generated[output_type] = CompleteContentOutputAdaptor.to_generated_data(
            output
        )
        # Optionally, update status and append a new status detail if needed
        # Example: content.set_status(GeneratedContentStatus.CATEGORIZATION_COMPLETED, "Content updated.")
        return content
