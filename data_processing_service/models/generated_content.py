"""
Model for generated content.
"""

from ..dependencies import  ContentType, OutputType
from datetime import datetime
from typing import Dict
from dataclasses import dataclass, field

@dataclass
class GeneratedContent:
    """Model representing generated content from collected content."""
    collected_content_id: str
    content_type: ContentType
    generated: Dict[OutputType, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_generated_content(self, output_type: OutputType, content: str):
        """Add generated content for a specific output type."""
        self.generated[output_type] = content
        self.updated_at = datetime.utcnow()