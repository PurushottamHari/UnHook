from typing import List


class CompleteContentInput:
    def __init__(
        self, title: str, content: str, language: str, tags: List[str], category: str
    ):
        self.title = title
        self.content = content
        self.language = language
        self.tags = tags
        self.category = category
