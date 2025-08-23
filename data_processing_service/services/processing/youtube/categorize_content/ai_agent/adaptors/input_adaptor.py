from typing import List

from data_processing_service.models.generated_content import GeneratedContent
from data_processing_service.services.processing.youtube.categorize_content.ai_agent.models.input import (
    CategorizationDataInput,
)


class CategorizationInputAdaptor:
    @staticmethod
    def from_generated_content_list(
        generated_content_list: List[GeneratedContent],
    ) -> List[CategorizationDataInput]:
        inputs = []
        for content in generated_content_list:
            title = ""
            short_summary = ""
            if content.generated and "VERY_SHORT" in content.generated:
                title = content.generated["VERY_SHORT"].string
            if content.generated and "SHORT" in content.generated:
                short_summary = content.generated["SHORT"].string
            if not title or not short_summary:
                raise ValueError(
                    f"Either title or short_summary is empty for content id: {content.id}"
                )
            inputs.append(
                CategorizationDataInput(
                    id=content.id, title=title, short_summary=short_summary
                )
            )
        return inputs
