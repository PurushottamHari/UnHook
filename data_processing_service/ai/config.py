"""
Configuration settings for AI services.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class ModelProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class ModelConfig(BaseModel):
    """Configuration for AI model settings."""
    provider: ModelProvider = Field(default=ModelProvider.DEEPSEEK)
    model_name: str = Field(default="deepseek-chat")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1000)
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    additional_params: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_deepseek_config(
        cls,
        model_name: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **additional_params
    ) -> "ModelConfig":
        """Create a DeepSeek-specific configuration."""
        return cls(
            provider=ModelProvider.DEEPSEEK,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            api_base=api_base,
            additional_params=additional_params
        )

    @classmethod
    def create_openai_config(
        cls,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        **additional_params
    ) -> "ModelConfig":
        """Create an OpenAI-specific configuration."""
        return cls(
            provider=ModelProvider.OPENAI,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            additional_params=additional_params
        )

# Create a singleton instance
model_config = ModelConfig() 