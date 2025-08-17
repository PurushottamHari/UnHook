import json
import os
from typing import List

from data_processing_service.ai import BaseAIClient, ModelConfig, ModelProvider
from data_processing_service.models.generated_content import GeneratedContent
from user_service.models.enums import CategoryName, ShelfLife

from .adaptors.input_adaptor import CategorizationInputAdaptor
from .adaptors.output_adaptor import CategorizationOutputAdaptor
from .models.input import CategorizationDataInput
from .models.output import CategorizationDataOutput


class CategorizationAgent(BaseAIClient[CategorizationDataOutput]):
    """AI agent for categorizing YouTube content."""

    def __init__(self):
        model_config = ModelConfig.create_deepseek_config(
            model_name="deepseek-chat", temperature=0.5
        )
        log_dir = os.path.join(os.path.dirname(__file__), "generated")
        super().__init__(CategorizationDataOutput, model_config, log_dir=log_dir)
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

    @staticmethod
    def _get_categories_list() -> List[str]:
        return [c.value for c in CategoryName]

    @staticmethod
    def _get_shelf_lives_list() -> List[str]:
        return [s.value for s in ShelfLife]

    async def categorize_content(
        self, generated_content_list: List[GeneratedContent]
    ) -> List[GeneratedContent]:
        inputs = CategorizationInputAdaptor.from_generated_content_list(
            generated_content_list
        )
        prompt = self._create_prompt(inputs)
        output = await self.generate_structured_response(user_input=prompt)
        updated = CategorizationOutputAdaptor.update_generated_content_with_categories(
            generated_content_list, output
        )
        return updated

    def _create_prompt(self, inputs: List[CategorizationDataInput]) -> str:
        return self._generation_prompt_template.format(
            content_items=json.dumps([i.model_dump() for i in inputs], indent=2),
            categories_list=json.dumps(self._get_categories_list()),
            shelf_lives=json.dumps(self._get_shelf_lives_list()),
        )

    def _create_output_format_guide(self) -> str:
        return self._output_format_guide
