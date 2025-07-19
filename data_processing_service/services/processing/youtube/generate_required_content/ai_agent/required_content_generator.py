import json
import os

from data_collector_service.collectors.youtube.models.youtube_video_details import \
    YouTubeVideoDetails
from data_processing_service.ai import BaseAIClient, ModelConfig, ModelProvider
from data_processing_service.models.generated_content import GeneratedData
from data_processing_service.models.youtube.subtitle_data import SubtitleMap

from .adaptors.input_adaptor import ContentInputAdaptor
from .adaptors.output_adaptor import ContentOutputAdaptor
from .models.input import ContentDataInput
from .models.output import ContentDataOutput


class RequiredContentGenerator(BaseAIClient[ContentDataOutput]):
    """AI agent for content generation."""

    def __init__(self):
        model_config = ModelConfig.create_deepseek_config(
            model_name="deepseek-chat", temperature=0.5
        )
        log_dir = os.path.join(os.path.dirname(__file__), "generated")
        super().__init__(ContentDataOutput, model_config, log_dir=log_dir)
        self._load_prompts()

    def _load_prompts(self):
        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        with open(os.path.join(prompts_dir, "system_prompt.txt"), "r") as f:
            self._system_prompt = f.read().strip()
        with open(os.path.join(prompts_dir, "generation_prompt.txt"), "r") as f:
            self._generation_prompt_template = f.read().strip()
        with open(os.path.join(prompts_dir, "output_prompt.txt"), "r") as f:
            self._output_format_guide = f.read().strip()

    def get_system_prompt(self) -> str:
        return self._system_prompt

    async def generate_required_content(
        self, youtube_video_details: YouTubeVideoDetails, subtitle_map: SubtitleMap
    ) -> dict[str, GeneratedData]:
        content_input = ContentInputAdaptor.from_youtube_details_and_subtitle_map(
            youtube_video_details, subtitle_map
        )
        prompt = self._create_prompt(content_input)
        content_output = await self.generate_structured_response(user_input=prompt)
        return ContentOutputAdaptor.to_generated_data_dict(content_output)

    def _create_prompt(self, content_input: ContentDataInput) -> str:
        input_data_no_subtitles = content_input.model_dump(
            exclude={"subtitle_data_input"}
        )
        return self._generation_prompt_template.format(
            youtube_video_data=json.dumps(input_data_no_subtitles, indent=2),
            language=content_input.subtitle_data_input.language,
            subtitles=content_input.subtitle_data_input.subtitle_string,
        )

    def _create_output_format_guide(self) -> str:
        return self._output_format_guide
