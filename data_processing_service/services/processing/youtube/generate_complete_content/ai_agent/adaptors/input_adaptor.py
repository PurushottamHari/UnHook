from data_processing_service.models.generated_content import GeneratedContent

from ..models.input import CompleteContentInput


class CompleteContentInputAdaptor:
    @staticmethod
    def from_dict(data: dict) -> CompleteContentInput:
        return CompleteContentInput(
            title=data.get("title", ""),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            category=data.get("category", ""),
        )

    @staticmethod
    def from_generated_content(
        content: GeneratedContent, content_data: str, content_language: str
    ) -> CompleteContentInput:
        # Extract title, content, tags, and category from GeneratedContent
        title = ""
        tags = []
        category = ""
        # Try to get title and tags from generated or category fields
        if content.generated and "VERY_SHORT" in content.generated:
            title = content.generated["VERY_SHORT"].string
        if content.category is not None:
            category = (
                content.category.category.value
                if hasattr(content.category.category, "value")
                else str(content.category.category)
            )
            tags = content.category.category_tags

        return CompleteContentInput(
            title=title,
            content=content_data,
            language=content_language,
            tags=tags,
            category=category,
        )
