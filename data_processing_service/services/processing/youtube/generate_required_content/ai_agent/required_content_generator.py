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

    # Static variable to track chunked mode
    _is_chunked_mode = False

    def __init__(self):
        model_config = ModelConfig.create_deepseek_config(
            model_name="deepseek-chat", temperature=0.5
        )
        log_dir = os.path.join(os.path.dirname(__file__), "generated")
        super().__init__(ContentDataOutput, model_config, log_dir=log_dir)
        self._load_prompts()

    def _load_prompts(self):
        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")

        # Regular prompts
        with open(os.path.join(prompts_dir, "system_prompt.txt"), "r") as f:
            self._system_prompt = f.read().strip()
        with open(os.path.join(prompts_dir, "generation_prompt.txt"), "r") as f:
            self._generation_prompt_template = f.read().strip()
        with open(os.path.join(prompts_dir, "output_prompt.txt"), "r") as f:
            self._output_format_guide = f.read().strip()

        # Chunked prompts
        chunked_dir = os.path.join(prompts_dir, "chunked")
        with open(os.path.join(chunked_dir, "system_prompt.txt"), "r") as f:
            self._chunked_system_prompt = f.read().strip()
        with open(os.path.join(chunked_dir, "generation_prompt.txt"), "r") as f:
            self._chunked_generation_prompt_template = f.read().strip()
        with open(os.path.join(chunked_dir, "output_prompt.txt"), "r") as f:
            self._chunked_output_format_guide = f.read().strip()

    def get_system_prompt(self) -> str:
        # Automatically detect chunked mode by checking the static flag
        if self._is_chunked_mode:
            return self._chunked_system_prompt
        # Default to regular mode
        return self._system_prompt

    def _create_output_format_guide(self) -> str:
        # Automatically detect chunked mode by checking the static flag
        if self._is_chunked_mode:
            return self._chunked_output_format_guide
        # Default to regular mode
        return self._output_format_guide

    async def generate_required_content(
        self, youtube_video_details: YouTubeVideoDetails, subtitle_map: SubtitleMap
    ) -> dict[str, GeneratedData]:
        content_input = ContentInputAdaptor.from_youtube_details_and_subtitle_map(
            youtube_video_details, subtitle_map
        )

        # Check if we need to chunk the content
        regular_prompt = self._create_prompt(content_input)
        is_chunked = self.should_chunk(
            content_input.subtitle_data_input.subtitle_string, regular_prompt
        )

        if is_chunked:
            # Set chunked mode flag and chunk the subtitles
            RequiredContentGenerator._is_chunked_mode = True
            try:
                # Chunk subtitles to fit within token limits
                max_chunk, excess_character_count = self.chunk_subtitles(
                    content_input.subtitle_data_input.subtitle_string,
                    self._chunked_generation_prompt_template,
                    youtube_video_data=json.dumps(
                        content_input.model_dump(exclude={"subtitle_data_input"}),
                        indent=2,
                    ),
                    language=content_input.subtitle_data_input.language,
                )

                # Update the subtitle data with the chunked version (incomplete subtitle chunk)
                content_input.subtitle_data_input.subtitle_string = max_chunk
                prompt = self._create_prompt(content_input, excess_character_count)
                output = await self.generate_structured_response(user_input=prompt)
            finally:
                # Reset the chunked mode flag
                RequiredContentGenerator._is_chunked_mode = False
        else:
            output = await self.generate_structured_response(user_input=regular_prompt)

        return ContentOutputAdaptor.to_generated_data_dict(output)

    def _create_prompt(
        self, content_input: ContentDataInput, excess_character_count: int = None
    ) -> str:
        input_data_no_subtitles = content_input.model_dump(
            exclude={"subtitle_data_input"}
        )

        # Use appropriate prompt template based on chunked mode
        if self._is_chunked_mode:
            return self._chunked_generation_prompt_template.format(
                youtube_video_data=json.dumps(input_data_no_subtitles, indent=2),
                language=content_input.subtitle_data_input.language,
                subtitles=content_input.subtitle_data_input.subtitle_string,
                excess_character_count=excess_character_count,
            )
        else:
            return self._generation_prompt_template.format(
                youtube_video_data=json.dumps(input_data_no_subtitles, indent=2),
                language=content_input.subtitle_data_input.language,
                subtitles=content_input.subtitle_data_input.subtitle_string,
            )

    def _calculate_total_tokens_for_content(self, content: str, prompt: str) -> int:
        """Calculate total tokens (prompt + estimated output) for given content and prompt."""
        prompt_tokens = self.get_estimated_tokens(prompt)
        # Calculate expected output tokens for max title (12 words) and max summary (200 words)
        max_title = "This is a maximum length title with exactly twelve words for testing purposes"
        max_summary = (
            "This is a maximum length summary with exactly two hundred words. " * 10
        )  # Repeat to get ~200 words
        expected_output = (
            f'{{"generated": {{"TITLE": "{max_title}", "SUMMARY": "{max_summary}"}}}}'
        )
        output_tokens = self.get_estimated_tokens(expected_output)
        return prompt_tokens + output_tokens

    def should_chunk(self, content: str, prompt: str) -> bool:
        """Check if content needs to be chunked based on token limits."""
        # Construct the complete prompt including system prompt and output format guide
        # Use regular prompts for initial check (not chunked mode yet)
        complete_prompt = (
            f"{self._system_prompt}\n\n{self._output_format_guide}\n\n{prompt}"
        )
        # Calculate total tokens including expected output (max title + max summary)
        total_tokens = self._calculate_total_tokens_for_content(
            content, complete_prompt
        )
        return total_tokens > self.model_config.max_tokens

    def chunk_subtitles(
        self, subtitles: str, prompt_template: str, **prompt_kwargs
    ) -> tuple[str, int]:
        """Chunk subtitles by truncating from the end to fit within token limits."""
        # Create the complete prompt with full subtitles
        # Provide a default excess_character_count for initial formatting
        prompt_kwargs_with_default = prompt_kwargs.copy()
        if "excess_character_count" not in prompt_kwargs_with_default:
            prompt_kwargs_with_default["excess_character_count"] = 0

        prompt = prompt_template.format(
            **prompt_kwargs_with_default, subtitles=subtitles
        )
        complete_prompt = f"{self._chunked_system_prompt}\n\n{self._chunked_output_format_guide}\n\n{prompt}"

        # Calculate total tokens including expected output
        total_tokens = self._calculate_total_tokens_for_content(
            subtitles, complete_prompt
        )

        # If already within limits, return full subtitles
        if total_tokens <= self.model_config.max_tokens:
            return subtitles, 0

        # Calculate how many tokens we need to reduce
        excess_tokens = total_tokens - self.model_config.max_tokens

        # Calculate how many characters correspond to the tokens we need to remove
        chars_to_remove = self.get_chars_for_tokens(excess_tokens)

        # Truncate subtitles from the end
        target_length = max(1, len(subtitles) - chars_to_remove)
        chunked_subtitles = subtitles[:target_length]

        # Calculate excess character count
        excess_character_count = len(subtitles) - len(chunked_subtitles)

        return chunked_subtitles, excess_character_count
