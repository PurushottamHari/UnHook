import os
from typing import Any

from data_processing_service.ai import BaseAIClient, ModelConfig


class ChunkSummarizer(BaseAIClient[str]):
    """AI agent for summarizing article chunks in multi-shot generation."""

    def __init__(self):
        model_config = ModelConfig.create_deepseek_config(
            model_name="deepseek-chat", temperature=0.3
        )
        log_dir = os.path.join(os.path.dirname(__file__), "generated")
        super().__init__(str, model_config, log_dir=log_dir)
        self._load_prompts()

    def _load_prompts(self):
        prompts_dir = os.path.join(
            os.path.dirname(__file__), "prompts", "summarize_chunk"
        )
        with open(os.path.join(prompts_dir, "system_prompt.txt"), "r") as f:
            self._system_prompt = f.read().strip()
        with open(os.path.join(prompts_dir, "generation_prompt.txt"), "r") as f:
            self._generation_prompt = f.read().strip()
        with open(os.path.join(prompts_dir, "output_prompt.txt"), "r") as f:
            self._output_format_guide = f.read().strip()

    def get_system_prompt(self) -> str:
        return self._system_prompt

    def _create_output_format_guide(self) -> str:
        return self._output_format_guide

    async def summarize_chunk(self, article_chunk: str) -> str:
        """Summarize an article chunk for use as context in the next generation step."""
        prompt = self._generation_prompt.format(article_chunk_content=article_chunk)
        return await self.generate_structured_response(user_input=prompt)
