import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class WebpageStatus(str, Enum):
    COLLECTED = "collected"


@dataclass
class WebpageStatusDetail:
    status: WebpageStatus
    created_at: datetime
    reason: str = ""


class WebpageCollectedContent:
    """Model class for storing webpage collected content details."""

    def __init__(
        self,
        id: str,
        sha: str,
        url: str,
        title: str,
        webpage_content: str,
        language: str,
        category_name: str,
        status: WebpageStatus,
        status_details: List[WebpageStatusDetail] = None,
        created_at: datetime = None,
        content_created_at: datetime = None,
        version: int = 1,
    ):
        self.id = id
        self.sha = sha
        self.url = url
        self.title = title
        self.webpage_content = webpage_content
        self.language = language
        self.category_name = category_name
        self.status = status
        self.status_details = status_details or []
        self.created_at = created_at or datetime.utcnow()
        self.content_created_at = content_created_at or datetime.utcnow()
        self.version = version
        if not status_details and self.status:
            self.set_status(self.status, "Initial status")

    def set_status(
        self,
        status: WebpageStatus,
        reason: str = "",
    ):
        """Set the status of the webpage and add a detail entry."""
        # NOTE: Do NOT increment version here.
        status_detail = WebpageStatusDetail(
            status=status, created_at=datetime.utcnow(), reason=reason
        )
        self.status_details.append(status_detail)
        self.status = status

    def to_dict(self) -> dict:
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "sha": self.sha,
            "url": self.url,
            "title": self.title,
            "webpage_content": self.webpage_content,
            "language": self.language,
            "category_name": self.category_name,
            "status": self.status.value,
            "status_details": [
                {
                    "status": detail.status.value,
                    "created_at": detail.created_at.isoformat(),
                    "reason": detail.reason,
                }
                for detail in self.status_details
            ],
            "created_at": self.created_at.isoformat(),
            "content_created_at": self.content_created_at.isoformat(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WebpageCollectedContent":
        """Create a model instance from a dictionary."""
        return cls(
            id=data["id"],
            sha=data["sha"],
            url=data["url"],
            title=data["title"],
            webpage_content=data["webpage_content"],
            language=data["language"],
            category_name=data["category_name"],
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else None
            ),
            content_created_at=(
                datetime.fromisoformat(data["content_created_at"])
                if "content_created_at" in data
                else None
            ),
            status=WebpageStatus(data["status"]),
            status_details=[
                WebpageStatusDetail(
                    status=WebpageStatus(detail["status"]),
                    created_at=datetime.fromisoformat(detail["created_at"]),
                    reason=detail.get("reason", ""),
                )
                for detail in data.get("status_details", [])
            ],
            version=data.get("version", 1),
        )
