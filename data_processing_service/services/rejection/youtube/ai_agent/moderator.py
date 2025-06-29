"""
Content moderation agent implementation.
"""

import json
import os
from typing import List

from data_processing_service.ai import BaseAIClient, ModelConfig, ModelProvider

from .models import ContentItem, ModerationInput, ModerationOutput


class ContentModerator(BaseAIClient[ModerationOutput]):
    """AI agent for content moderation."""

    def __init__(self):
        model_config = ModelConfig.create_deepseek_config(
            model_name="deepseek-chat",
            temperature=0.2,  # Lower temperature for more consistent moderation
            api_key="sk-359ed2eb7c13455e827b557cece76038",
        )
        log_dir = os.path.join(os.path.dirname(__file__), "generated")
        super().__init__(ModerationOutput, model_config, log_dir=log_dir)
        self._load_prompts()

    def _load_prompts(self):
        """Load prompt templates from files."""
        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")

        with open(os.path.join(prompts_dir, "system_prompt.txt"), "r") as f:
            self._system_prompt = f.read().strip()

        with open(os.path.join(prompts_dir, "moderation_prompt.txt"), "r") as f:
            self._moderation_prompt_template = f.read().strip()

        with open(os.path.join(prompts_dir, "output_prompt.txt"), "r") as f:
            self._output_format_guide = f.read().strip()

    def get_system_prompt(self) -> str:
        return self._system_prompt

    async def moderate_content(
        self, moderation_input: ModerationInput
    ) -> ModerationOutput:
        """Moderate a list of content items and return rejected items with reasons."""
        prompt = self._create_prompt(
            moderation_input.items, moderation_input.filter_preferences
        )
        return await self.generate_structured_response(user_input=prompt)

    def _create_prompt(
        self, items: List[ContentItem], filter_preferences: List[str]
    ) -> str:
        """Create a prompt for content moderation."""
        input_data = ModerationInput(items=items, filter_preferences=filter_preferences)

        return self._moderation_prompt_template.format(
            filter_preferences=", ".join(filter_preferences),
            content_items=json.dumps(input_data.model_dump(), indent=2),
        )

    def _create_output_format_guide(self) -> str:
        return self._output_format_guide
