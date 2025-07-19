from typing import List

from data_processing_service.models.generated_content import (CategoryInfo,
                                                              GeneratedContent)
from user_service.models.enums import CategoryName

from ..models.output import CategorizationDataOutput, CategoryOutputItem


class CategorizationOutputAdaptor:
    @staticmethod
    def update_generated_content_with_categories(
        generated_content_list: List[GeneratedContent],
        output: CategorizationDataOutput,
    ) -> List[GeneratedContent]:
        # Map id to GeneratedContent for fast lookup
        id_to_content = {content.id: content for content in generated_content_list}
        for item in output.output:
            content = id_to_content.get(item.id)
            if content:
                content.category = CategoryInfo(
                    category=CategoryName(item.category),
                    category_description=item.category_description,
                    category_tags=item.category_tags,
                )
        return generated_content_list
