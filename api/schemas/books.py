from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..utils.utils import ALLOWED_EXTENSIONS


class BookRequest(BaseModel):
    file_path: str = Field(min_length=1, max_length=1000)

    @field_validator("file_path")
    def validate_file_extension(cls, value):
        if not any(value.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValueError()
        return value

    model_config = ConfigDict(str_strip_whitespace=True)


class BookResponse(BaseModel):
    id: UUID
    title: str
    file_path: str
