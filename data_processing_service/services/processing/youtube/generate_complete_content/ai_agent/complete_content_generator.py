import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from data_processing_service.ai import BaseAIClient, ModelConfig, ModelProvider
from data_processing_service.models.generated_content import (
    GeneratedContent,
    GeneratedContentStatus,
    StatusDetail,
)
from data_processing_service.services.processing.youtube.generate_complete_content.ai_agent.adaptors.input_adaptor import (
    CompleteContentInputAdaptor,
)
from data_processing_service.services.processing.youtube.generate_complete_content.ai_agent.adaptors.output_adaptor import (
    CompleteContentOutputAdaptor,
)
from data_processing_service.services.processing.youtube.generate_complete_content.ai_agent.chunk_summarizer import (
    ChunkSummarizer,
)
from data_processing_service.services.processing.youtube.generate_complete_content.ai_agent.models.input import (
    CompleteContentInput,
)
from user_service.models.enums import OutputType


class CompleteContentGenerator(BaseAIClient[str]):
    """AI agent for generating complete newspaper-style content."""

    # Configurable factor for output token estimation
    OUTPUT_TOKEN_FACTOR = 1.3

    # Static variable to track current stage for multi-shot generation
    _current_stage = None

    def __init__(self):
        model_config = ModelConfig.create_deepseek_config(
            model_name="deepseek-chat", temperature=0.5
        )
        log_dir = os.path.join(os.path.dirname(__file__), "generated")
        super().__init__(str, model_config, log_dir=log_dir)
        self._load_prompts()
        self.chunk_summarizer = ChunkSummarizer()

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

    def get_system_prompt(self) -> str:
        # Automatically detect multi-shot mode by checking the static stage variable
        if self._current_stage is not None:
            # We're in multi-shot mode, use the appropriate stage
            if self._current_stage == "beginning":
                return self._beginning_system_prompt
            elif self._current_stage == "transient":
                return self._transient_system_prompt
            elif self._current_stage == "final":
                return self._final_system_prompt
            else:
                raise ValueError(f"Invalid stage: {self._current_stage}")
        # Default to one-shot mode
        return self._one_shot_system_prompt

    def _create_output_format_guide(self) -> str:
        # Automatically detect multi-shot mode by checking the static stage variable
        if self._current_stage is not None:
            # We're in multi-shot mode, use the appropriate stage
            if self._current_stage == "beginning":
                return self._beginning_output_format_guide
            elif self._current_stage == "transient":
                return self._transient_output_format_guide
            elif self._current_stage == "final":
                return self._final_output_format_guide
            else:
                raise ValueError(f"Invalid stage: {self._current_stage}")
        # Default to one-shot mode
        return self._one_shot_output_format_guide

    def _calculate_character_count(self, content: str) -> int:
        """Calculate the target character count for the article based on content length and OUTPUT_TOKEN_FACTOR."""
        content_tokens = self.get_estimated_tokens(content)
        # Estimate characters per token (rough approximation: 4 characters per token)
        chars_per_token = 4
        target_tokens = int(content_tokens * self.OUTPUT_TOKEN_FACTOR)
        return target_tokens * chars_per_token

    def _calculate_total_tokens_for_content(self, content: str, prompt: str) -> int:
        """Calculate total tokens (prompt + estimated output) for given content and prompt."""
        prompt_tokens = self.get_estimated_tokens(prompt)
        content_tokens = self.get_estimated_tokens(content)
        max_output_tokens = max(1, int(content_tokens * self.OUTPUT_TOKEN_FACTOR))
        return prompt_tokens + max_output_tokens

    def _is_content_within_token_limit(
        self, content: str, prompt_template: str, **prompt_kwargs
    ) -> bool:
        """Check if content fits within token limits when formatted with the given prompt template."""
        prompt = prompt_template.format(**prompt_kwargs, content=content)
        complete_prompt = f"{self.get_system_prompt()}\n\n{self._create_output_format_guide()}\n\n{prompt}"
        total_tokens = self._calculate_total_tokens_for_content(
            content, complete_prompt
        )
        return total_tokens <= self.model_config.max_tokens

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
            print("Generating one-shot content...")
            output = await self.generate_structured_response(user_input=one_shot_prompt)
            output_type = OutputType.MEDIUM
        return CompleteContentOutputAdaptor.update_generated_content(
            content, output, output_type
        )

    async def _generate_multi_shot(self, input_data: CompleteContentInput) -> str:
        # Use the beginning prompt for chunking
        # Calculate character count for the full content for chunking purposes
        full_character_count = self._calculate_character_count(input_data.content)
        chunks = self.chunk_content(
            input_data.content,
            self._beginning_prompt,
            title=input_data.title,
            language=input_data.language,
            tags=", ".join(input_data.tags),
            category=input_data.category,
            character_count=full_character_count,
            chunk_number=1,
        )
        total_chunks = len(chunks)
        print(f"Generating multi-shot content in {total_chunks} chunks...")
        article_parts = []
        summary_of_previous_chunks = None
        for idx, chunk in enumerate(chunks):
            # Calculate character count based on this specific chunk
            print(f"Generating chunk {idx + 1} of {total_chunks}...")
            chunk_character_count = self._calculate_character_count(chunk)

            if idx == 0:
                CompleteContentGenerator._current_stage = "beginning"
                prompt = self._beginning_prompt.format(
                    title=input_data.title,
                    content=chunk,
                    chunk_number=idx + 1,
                    total_chunks=total_chunks,
                    language=input_data.language,
                    tags=", ".join(input_data.tags),
                    category=input_data.category,
                    character_count=chunk_character_count,
                )
            elif idx == len(chunks) - 1:
                CompleteContentGenerator._current_stage = "final"
                prompt = self._final_prompt.format(
                    title=input_data.title,
                    content=chunk,
                    chunk_number=idx + 1,
                    total_chunks=total_chunks,
                    language=input_data.language,
                    tags=", ".join(input_data.tags),
                    category=input_data.category,
                    summary_of_previous_chunks=summary_of_previous_chunks,
                    character_count=chunk_character_count,
                )
            else:
                CompleteContentGenerator._current_stage = "transient"
                prompt = self._transient_prompt.format(
                    title=input_data.title,
                    content=chunk,
                    language=input_data.language,
                    tags=", ".join(input_data.tags),
                    category=input_data.category,
                    summary_of_previous_chunks=summary_of_previous_chunks,
                    chunk_number=idx + 1,
                    total_chunks=total_chunks,
                    character_count=chunk_character_count,
                )
            response = await self.generate_structured_response(user_input=prompt)
            article_parts.append(response)

            # Summarize this chunk for the next iteration (except for the last chunk)
            if idx < len(chunks) - 1:
                summary_of_previous_chunks = (
                    await self.chunk_summarizer.summarize_chunk(response)
                )

        # Reset the static stage variable after multi-shot generation is complete
        CompleteContentGenerator._current_stage = None
        return "\n".join(article_parts)

    def should_chunk(self, content: str, prompt: str) -> bool:
        # Construct the complete prompt including system prompt and output format guide
        complete_prompt = f"{self.get_system_prompt()}\n\n{self._create_output_format_guide()}\n\n{prompt}"
        total_tokens = self._calculate_total_tokens_for_content(
            content, complete_prompt
        )
        return total_tokens > self.model_config.max_tokens

    def chunk_content(
        self, content: str, prompt_template: str, **prompt_kwargs
    ) -> List[str]:
        content_len = len(content)

        # Binary search to find the optimal number of chunks
        low, high = 1, content_len
        best_num_chunks = 1

        while low <= high:
            mid = (low + high) // 2
            chunk_size = content_len // mid

            # Test if this number of chunks works
            valid_config = True
            for i in range(mid):
                start = i * chunk_size
                end = start + chunk_size if i < mid - 1 else content_len
                chunk = content[start:end]

                # Create a copy of prompt_kwargs and add missing parameters for validation
                validation_kwargs = prompt_kwargs.copy()
                if "total_chunks" not in validation_kwargs:
                    validation_kwargs["total_chunks"] = mid
                if "chunk_number" not in validation_kwargs:
                    validation_kwargs["chunk_number"] = i + 1

                if not self._is_content_within_token_limit(
                    chunk, prompt_template, **validation_kwargs
                ):
                    valid_config = False
                    break

            if valid_config:
                # This number of chunks works, try to find a better (smaller) number
                best_num_chunks = mid
                high = mid - 1
            else:
                # Too many chunks, try fewer
                high = mid - 1

        # Create the chunks with the best number found
        chunk_size = content_len // best_num_chunks
        chunks = []
        for i in range(best_num_chunks):
            start = i * chunk_size
            end = start + chunk_size if i < best_num_chunks - 1 else content_len
            chunks.append(content[start:end])

        return chunks


async def test_generation():
    """Test function to generate complete content for a specific generated content ID."""
    # Import necessary modules for testing
    from data_collector_service.models.enums import ContentType
    from data_collector_service.models.user_collected_content import ContentStatus
    from data_processing_service.models.generated_content import GeneratedContentStatus
    from data_processing_service.repositories.ephemeral.local.youtube_content_ephemeral_repository import (
        LocalYoutubeContentEphemeralRepository,
    )
    from data_processing_service.repositories.mongodb.config.database import MongoDB
    from data_processing_service.repositories.mongodb.user_content_repository import (
        MongoDBUserContentRepository,
    )
    from data_processing_service.services.processing.youtube.process_moderated_content.subtitles.utils.subtitle_utils import (
        SubtitleUtils,
    )

    # Hardcoded generated content ID for testing
    generated_content_id = (
        "c79f9fd9-ab1a-4197-a7bd-b3a64c261260"  # Replace with your actual ID
    )

    try:
        # Initialize MongoDB connection if not already connected
        if MongoDB.db is None:
            MongoDB.connect_to_database()

        # Create repositories and utilities
        youtube_content_ephemeral_repository = LocalYoutubeContentEphemeralRepository()
        subtitle_utils = SubtitleUtils()
        complete_content_generator = CompleteContentGenerator()

        # Fetch the specific generated content directly from MongoDB
        db = MongoDB.get_database()
        generated_content_collection = db["generated_content"]
        content_doc = generated_content_collection.find_one(
            {"_id": generated_content_id}
        )

        if not content_doc:
            print(f"Generated content with ID {generated_content_id} not found.")
            return

        # Convert MongoDB document to DB model first, then to GeneratedContent object
        from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import (
            GeneratedContentAdapter,
        )
        from data_processing_service.repositories.mongodb.models.generated_content_db_model import (
            GeneratedContentDBModel,
        )

        content_db_model = GeneratedContentDBModel(**content_doc)
        content = GeneratedContentAdapter.from_generated_content_db_model(
            content_db_model
        )

        print(f"Found generated content: {content.id}")
        print(f"External ID: {content.external_id}")
        print(f"Current status: {content.status}")

        # Fetch the corresponding user collected content directly from MongoDB
        user_collected_content_collection = db["collected_content"]
        user_collected_content_doc = user_collected_content_collection.find_one(
            {"external_id": content.external_id}
        )

        if not user_collected_content_doc:
            print(
                f"User collected content for external ID {content.external_id} not found."
            )
            return

        # Convert MongoDB document to DB model first, then to UserCollectedContent object
        from data_collector_service.repositories.mongodb.adapters.collected_content_adapter import (
            CollectedContentAdapter,
        )
        from data_collector_service.repositories.mongodb.models.collected_content_db_model import (
            CollectedContentDBModel,
        )

        user_collected_content_db_model = CollectedContentDBModel(
            **user_collected_content_doc
        )
        user_collected_content = CollectedContentAdapter.to_user_collected_content(
            user_collected_content_db_model
        )

        print(f"Found user collected content: {user_collected_content.id}")

        # Get YouTube video details
        youtube_video_details = user_collected_content.data.get(
            ContentType.YOUTUBE_VIDEO
        )
        if not youtube_video_details:
            print(
                f"YouTube video details not found for external ID {content.external_id}."
            )
            return

        # Get subtitle data
        subtitle_data = (
            youtube_content_ephemeral_repository.get_all_clean_subtitle_file_data(
                video_id=content.external_id
            )
        )

        # Check if clean subtitles are available
        if not subtitle_data.manual and not subtitle_data.automatic:
            print(f"No clean subtitles found for video_id {content.external_id}.")
            return

        # Select the best subtitle
        selected_subtitle = subtitle_utils.select_best_subtitle(
            subtitle_data, youtube_video_details
        )

        print(f"Selected subtitle language: {selected_subtitle.language}")
        print(f"Subtitle length: {len(selected_subtitle.subtitle)} characters")

        # Generate the complete content
        print("Generating complete content...")
        updated_content = (
            await complete_content_generator.generate_for_generated_content(
                content=content,
                content_data=selected_subtitle.subtitle,
                content_language=selected_subtitle.language,
            )
        )

        # Print the generated content
        print("\n" + "=" * 50)
        print("GENERATED CONTENT")
        print("=" * 50)
        print(f"Title: {updated_content.generated.get('VERY_SHORT', 'N/A')}")
        print(
            f"Category: {updated_content.category.category.value if updated_content.category else 'N/A'}"
        )

        # Print the final article content
        if "LONG" in updated_content.generated:
            print(
                f"\nLong Content Length: {len(updated_content.generated['LONG'].string)} characters"
            )
            print("\n" + "=" * 50)
            print("FINAL ARTICLE")
            print("=" * 50)
            print(updated_content.generated["LONG"].string)
            print("=" * 50)

            # Write the final article to a test file
            test_output_dir = os.path.join(os.path.dirname(__file__), "generated")
            os.makedirs(test_output_dir, exist_ok=True)
            output_file_path = os.path.join(
                test_output_dir, f"article_{content.external_id}.txt"
            )
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(updated_content.generated["LONG"].string)
            print(f"\nArticle saved to: {output_file_path}")

        elif "MEDIUM" in updated_content.generated:
            print(
                f"\nMedium Content Length: {len(updated_content.generated['MEDIUM'].string)} characters"
            )
            print("\n" + "=" * 50)
            print("FINAL ARTICLE")
            print("=" * 50)
            print(updated_content.generated["MEDIUM"].string)
            print("=" * 50)

            # Write the final article to a test file
            test_output_dir = os.path.join(
                os.path.dirname(__file__),
                "generated",
            )
            os.makedirs(test_output_dir, exist_ok=True)
            output_file_path = os.path.join(
                test_output_dir, f"article_{content.external_id}.txt"
            )
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(updated_content.generated["MEDIUM"].string)
            print(f"\nArticle saved to: {output_file_path}")

        else:
            print("\nNo article content found in generated data.")

        print("\n" + "=" * 50)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 50)

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()
