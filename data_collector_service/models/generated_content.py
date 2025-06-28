from datetime import datetime
from typing import Dict
from dataclasses import dataclass, field
from .enums import ContentType
from user_service.models.enums import OutputType

@dataclass
class GeneratedContent:
    content_type: ContentType
    external_id: str
    generated: Dict[OutputType, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_generated_content(self, output_type: OutputType, content: str):
        self.generated[output_type] = content
        self.updated_at = datetime.utcnow() 