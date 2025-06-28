"""
Base AI client implementation supporting multiple model providers.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type
from pydantic import BaseModel
from langchain_deepseek import ChatDeepSeek
from langchain.schema import HumanMessage, SystemMessage
from .config import ModelConfig, ModelProvider
from datetime import datetime
import os

T = TypeVar('T', bound=BaseModel)

class BaseAIClient(Generic[T], ABC):
    """Base class for AI clients with structured output support."""
    
    def __init__(self, output_model: Type[T], model_config: ModelConfig, log_dir: Optional[str] = None):
        self.output_model = output_model
        self.model_config = model_config
        self.llm = self._initialize_llm()
        self.log_dir = log_dir
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on the provider."""
        if self.model_config.provider == ModelProvider.DEEPSEEK:
            return ChatDeepSeek(
                model_name=self.model_config.model_name,
                temperature=self.model_config.temperature,
                max_tokens=self.model_config.max_tokens,
                api_key=self.model_config.api_key,
                **self.model_config.additional_params
            )
        elif self.model_config.provider == ModelProvider.OPENAI:
            return ChatOpenAI(
                model_name=self.model_config.model_name,
                temperature=self.model_config.temperature,
                max_tokens=self.model_config.max_tokens,
                openai_api_key=self.model_config.api_key,
                **self.model_config.additional_params
            )
        # Add other providers as needed
        raise ValueError(f"Unsupported model provider: {self.model_config.provider}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for the specific use case."""
        pass

    @abstractmethod
    def _create_output_format_guide(self) -> str:
        """Create a guide for the expected output format."""
        pass
    
    async def generate_structured_response(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """Generate a response and parse it into the specified output model."""
        messages = [
            SystemMessage(content=f"{self.get_system_prompt()}\n\n{self._create_output_format_guide()}"),
            HumanMessage(content=user_input)
        ]

        log_file_path = None
        if self.log_dir:
            os.makedirs(self.log_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            log_file_path = os.path.join(self.log_dir, f"prompt_response_{timestamp}.txt")
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write("--- PROMPT ---\n")
                for m in messages:
                    f.write(f"{type(m).__name__}: {m.content}\n\n")

        response = await self.llm.agenerate([messages])
        response_text = response.generations[0][0].text

        if log_file_path:
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write("--- RAW RESPONSE ---\n")
                f.write(response_text + "\n")
        try:
            # Parse the response into the output model
            return self.output_model.parse_raw(response_text)
        except Exception as e:
            raise ValueError(f"Failed to parse AI response into {self.output_model.__name__}: {str(e)}") 