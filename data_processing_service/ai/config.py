"""
Configuration settings for AI services.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Define the path outside the class
ENV_FILE_PATH = str(Path(__file__).parent.parent / ".env")


class AISettings(BaseSettings):
    DEEPSEEK_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    class Config:
        env_file = ENV_FILE_PATH
        case_sensitive = True
        extra = "ignore"


# Singleton instance
ai_settings = AISettings()


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
        max_tokens: int = 62000,  # 64k but tbs
        api_base: Optional[str] = None,
        **additional_params
    ) -> "ModelConfig":
        """Create a DeepSeek-specific configuration."""
        api_key = ai_settings.DEEPSEEK_API_KEY
        return cls(
            provider=ModelProvider.DEEPSEEK,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            api_base=api_base,
            additional_params=additional_params,
        )

    @classmethod
    def create_openai_config(
        cls,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **additional_params
    ) -> "ModelConfig":
        """Create an OpenAI-specific configuration."""
        api_key = ai_settings.OPENAI_API_KEY
        return cls(
            provider=ModelProvider.OPENAI,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            additional_params=additional_params,
        )

    @classmethod
    def create_anthropic_config(
        cls,
        model_name: str = "claude-v1",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **additional_params
    ) -> "ModelConfig":
        """Create an Anthropic-specific configuration."""
        api_key = ai_settings.ANTHROPIC_API_KEY
        return cls(
            provider=ModelProvider.ANTHROPIC,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            additional_params=additional_params,
        )


# Create a singleton instance
model_config = ModelConfig()
