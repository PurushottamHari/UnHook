from pydantic import BaseModel


class ContentDataOutput(BaseModel):
    generated: dict[str, str]
