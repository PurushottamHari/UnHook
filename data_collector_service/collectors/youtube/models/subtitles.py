from collections import UserDict

import langcodes


class SubtitleInfo(UserDict[str, str]):
    """Model for subtitle information, mapping extension to URL."""

    @classmethod
    def from_dict(cls, data: dict) -> "SubtitleInfo":
        return cls(data)

    def to_dict(self) -> dict[str, str]:
        return self.data


class SubtitleData(UserDict[str, SubtitleInfo]):
    """Model for a collection of subtitles for various languages."""

    def __setitem__(self, key: str, value: SubtitleInfo):
        if not langcodes.tag_is_valid(key):
            raise ValueError(f"'{key}' is not a valid language code.")
        super().__setitem__(key, value)

    @classmethod
    def from_dict(cls, data: dict) -> "SubtitleData":
        instance = cls()
        for lang, info_dict in data.items():
            instance[lang] = SubtitleInfo.from_dict(info_dict)
        return instance

    def to_dict(self) -> dict:
        return {lang: info.to_dict() for lang, info in self.items()}


class Subtitles:
    """Model for automatic and manual subtitles."""

    def __init__(self, automatic: SubtitleData, manual: SubtitleData):
        self.automatic = automatic
        self.manual = manual

    def to_dict(self) -> dict:
        return {"automatic": self.automatic.to_dict(), "manual": self.manual.to_dict()}

    @classmethod
    def from_dict(cls, data: dict) -> "Subtitles":
        automatic = SubtitleData.from_dict(data.get("automatic", {}))
        manual = SubtitleData.from_dict(data.get("manual", {}))
        return cls(automatic=automatic, manual=manual)

    def validate_not_empty(self):
        """
        Validates that there is at least one automatic or manual subtitle with a valid URL.
        Raises:
            ValueError: If no valid subtitles are found.
        """
        has_manual_subtitles = any(
            info and any(url for url in info.values()) for info in self.manual.values()
        )
        has_automatic_subtitles = any(
            info and any(url for url in info.values())
            for info in self.automatic.values()
        )

        if not has_manual_subtitles and not has_automatic_subtitles:
            raise ValueError(
                "Subtitles object must have at least one language with a valid subtitle URL."
            )
