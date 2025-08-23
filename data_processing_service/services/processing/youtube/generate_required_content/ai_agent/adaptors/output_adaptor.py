from typing import Dict

from data_processing_service.models.generated_content import GeneratedData
from data_processing_service.services.processing.youtube.generate_required_content.ai_agent.models.output import \
    ContentDataOutput
from user_service.models import OutputType


class ContentOutputAdaptor:
    @staticmethod
    def to_generated_data_dict(
        content_output: ContentDataOutput,
    ) -> Dict[str, GeneratedData]:
        result = {}
        for key, value in content_output.generated.items():
            if key == "TITLE":
                mapped_key = OutputType.VERY_SHORT
            elif key == "SUMMARY":
                mapped_key = OutputType.SHORT
            else:
                raise ValueError(f"Unexpected key in generated content: {key}")
            result[mapped_key] = GeneratedData(string=value)
        return result
