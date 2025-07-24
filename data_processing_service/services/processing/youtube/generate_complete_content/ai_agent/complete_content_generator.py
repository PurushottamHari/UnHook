import os
from datetime import datetime
from typing import List

from data_processing_service.ai import BaseAIClient, ModelConfig, ModelProvider
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus, StatusDetail)
from user_service.models.enums import OutputType

from .adaptors.input_adaptor import CompleteContentInputAdaptor
from .adaptors.output_adaptor import CompleteContentOutputAdaptor
from .models.input import CompleteContentInput


class CompleteContentGenerator(BaseAIClient[str]):
    """AI agent for generating complete newspaper-style content."""

    # Configurable factor for output token estimation
    OUTPUT_TOKEN_FACTOR = 1.3

    def __init__(self):
        model_config = ModelConfig.create_deepseek_config(
            model_name="deepseek-chat", temperature=0.5
        )
        log_dir = os.path.join(os.path.dirname(__file__), "generated")
        super().__init__(str, model_config, log_dir=log_dir)
        self._load_prompts()

    def _load_prompts(self):
        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        # One-shot prompts
        one_shot_dir = os.path.join(prompts_dir, "one_shot")
        with open(os.path.join(one_shot_dir, "system_prompt.txt"), "r") as f:
            self._one_shot_system_prompt = f.read().strip()
        with open(os.path.join(one_shot_dir, "generation_prompt.txt"), "r") as f:
            self._one_shot_prompt = f.read().strip()
        with open(os.path.join(one_shot_dir, "output_prompt.txt"), "r") as f:
            self._one_shot_output_format_guide = f.read().strip()
        # Multi-shot prompts (now organized by stage)
        multi_shot_dir = os.path.join(prompts_dir, "multi_shot")
        # Beginning
        beginning_dir = os.path.join(multi_shot_dir, "beginning")
        with open(os.path.join(beginning_dir, "system_prompt.txt"), "r") as f:
            self._beginning_system_prompt = f.read().strip()
        with open(os.path.join(beginning_dir, "generation_prompt.txt"), "r") as f:
            self._beginning_prompt = f.read().strip()
        with open(os.path.join(beginning_dir, "output_prompt.txt"), "r") as f:
            self._beginning_output_format_guide = f.read().strip()
        # Transient
        transient_dir = os.path.join(multi_shot_dir, "transient")
        with open(os.path.join(transient_dir, "system_prompt.txt"), "r") as f:
            self._transient_system_prompt = f.read().strip()
        with open(os.path.join(transient_dir, "generation_prompt.txt"), "r") as f:
            self._transient_prompt = f.read().strip()
        with open(os.path.join(transient_dir, "output_prompt.txt"), "r") as f:
            self._transient_output_format_guide = f.read().strip()
        # Final
        final_dir = os.path.join(multi_shot_dir, "final")
        with open(os.path.join(final_dir, "system_prompt.txt"), "r") as f:
            self._final_system_prompt = f.read().strip()
        with open(os.path.join(final_dir, "generation_prompt.txt"), "r") as f:
            self._final_prompt = f.read().strip()
        with open(os.path.join(final_dir, "output_prompt.txt"), "r") as f:
            self._final_output_format_guide = f.read().strip()

    def get_system_prompt(self, multi_shot: bool = False, stage: str = None) -> str:
        if not multi_shot:
            return self._one_shot_system_prompt
        if stage == "beginning":
            return self._beginning_system_prompt
        elif stage == "transient":
            return self._transient_system_prompt
        elif stage == "final":
            return self._final_system_prompt
        return self._one_shot_system_prompt

    def _create_output_format_guide(
        self, multi_shot: bool = False, stage: str = None
    ) -> str:
        if not multi_shot:
            return self._one_shot_output_format_guide
        if stage == "beginning":
            return self._beginning_output_format_guide
        elif stage == "transient":
            return self._transient_output_format_guide
        elif stage == "final":
            return self._final_output_format_guide
        return self._one_shot_output_format_guide

    def _calculate_character_count(self, content: str) -> int:
        """Calculate the target character count for the article based on content length and OUTPUT_TOKEN_FACTOR."""
        content_tokens = self.get_estimated_tokens(content)
        # Estimate characters per token (rough approximation: 4 characters per token)
        chars_per_token = 4
        target_tokens = int(content_tokens * self.OUTPUT_TOKEN_FACTOR)
        return target_tokens * chars_per_token

    async def generate_for_generated_content(
        self, content: GeneratedContent, content_data: str, content_language: str
    ) -> GeneratedContent:
        input_data = CompleteContentInputAdaptor.from_generated_content(
            content, content_data, content_language
        )
        character_count = self._calculate_character_count(input_data.content)
        one_shot_prompt = self._one_shot_prompt.format(
            title=input_data.title,
            content=input_data.content,
            language=input_data.language,
            tags=", ".join(input_data.tags),
            category=input_data.category,
            character_count=character_count,
        )
        is_multi_shot = self.should_chunk(input_data.content, one_shot_prompt)
        if is_multi_shot:
            output = await self._generate_multi_shot(input_data)
            output_type = OutputType.LONG
        else:
            output = await self.generate_structured_response(user_input=one_shot_prompt)
            output_type = OutputType.MEDIUM
        return CompleteContentOutputAdaptor.update_generated_content(
            content, output, output_type
        )

    async def _generate_multi_shot(self, input_data: CompleteContentInput) -> str:
        # Use the beginning prompt for chunking
        chunks = self.chunk_content(
            input_data.content,
            self._beginning_prompt,
            title=input_data.title,
            tags=", ".join(input_data.tags),
            category=input_data.category,
        )
        article_parts = []
        snippet = None
        for idx, chunk in enumerate(chunks):
            # Calculate character count based on this specific chunk
            chunk_character_count = self._calculate_character_count(chunk)

            if idx == 0:
                prompt = self._beginning_prompt.format(
                    title=input_data.title,
                    content=chunk,
                    language=input_data.language,
                    tags=", ".join(input_data.tags),
                    category=input_data.category,
                    character_count=chunk_character_count,
                )
            elif idx == len(chunks) - 1:
                prompt = self._final_prompt.format(
                    title=input_data.title,
                    content=chunk,
                    language=input_data.language,
                    tags=", ".join(input_data.tags),
                    category=input_data.category,
                    previous_snippet=snippet or "",
                    character_count=chunk_character_count,
                )
            else:
                prompt = self._transient_prompt.format(
                    title=input_data.title,
                    content=chunk,
                    language=input_data.language,
                    tags=", ".join(input_data.tags),
                    category=input_data.category,
                    previous_snippet=snippet or "",
                    chunk_number=idx + 1,
                    character_count=chunk_character_count,
                )
            response = await self.generate_structured_response(user_input=prompt)
            article_markdown = response
            if "\n---SNIPPET---\n" in article_markdown:
                article, snippet_val = article_markdown.split("\n---SNIPPET---\n", 1)
                article_parts.append(article)
                snippet = snippet_val
            else:
                article_parts.append(article_markdown)
                snippet = None
        return "\n".join(article_parts)

    def should_chunk(self, content: str, prompt: str) -> bool:
        # Construct the complete prompt including system prompt and output format guide
        complete_prompt = f"{self.get_system_prompt()}\n\n{self._create_output_format_guide()}\n\n{prompt}"

        content_tokens = self.get_estimated_tokens(content)
        complete_prompt_tokens = self.get_estimated_tokens(complete_prompt)
        max_output_tokens = max(1, int(content_tokens * self.OUTPUT_TOKEN_FACTOR))
        total_tokens = complete_prompt_tokens + max_output_tokens
        return total_tokens > self.model_config.max_tokens

    def chunk_content(
        self, content: str, prompt_template: str, **prompt_kwargs
    ) -> List[str]:
        content_len = len(content)
        chunks = []
        start = 0
        while start < content_len:
            low, high = 1, content_len - start
            best = low
            while low <= high:
                mid = (low + high) // 2
                chunk = content[start : start + mid]
                prompt = prompt_template.format(**prompt_kwargs, content=chunk)
                # Construct complete prompt for accurate token estimation
                complete_prompt = f"{self.get_system_prompt()}\n\n{self._create_output_format_guide()}\n\n{prompt}"
                content_tokens = self.get_estimated_tokens(chunk)
                complete_prompt_tokens = self.get_estimated_tokens(complete_prompt)
                max_output_tokens = max(
                    1, int(content_tokens * self.OUTPUT_TOKEN_FACTOR)
                )
                total_tokens = complete_prompt_tokens + max_output_tokens
                if total_tokens <= self.model_config.max_tokens:
                    best = mid
                    low = mid + 1
                else:
                    high = mid - 1
            chunk = content[start : start + best]
            chunks.append(chunk)
            start += best
        return chunks
