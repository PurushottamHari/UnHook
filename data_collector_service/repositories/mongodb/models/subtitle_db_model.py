from typing import Dict, Optional

from pydantic import BaseModel, RootModel


class SubtitleInfoDB(RootModel[Dict[str, str]]):
    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        return cls.model_validate(data)


class SubtitleDB(BaseModel):
    automatic: Optional[Dict[str, SubtitleInfoDB]] = None
    manual: Optional[Dict[str, SubtitleInfoDB]] = None
