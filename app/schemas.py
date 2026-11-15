import re

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    TypeAdapter,
    ValidationError,
    field_validator,
)


class PostingRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Message must not exceed 200 characters"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):

        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty")

        # Extract HTTP/HTTPS URLs
        urls = re.findall(
            r'https?://[^\s<>"\']+',
            value,
            flags=re.IGNORECASE
        )

        if len(urls) != 1:
            raise ValueError(
                "Message must contain exactly one CTA URL"
            )

        # Remove common sentence-ending punctuation
        url = urls[0].rstrip(".,!?;:)]}")

        try:
            TypeAdapter(HttpUrl).validate_python(url)

        except ValidationError:
            raise ValueError("Please provide a valid HTTP/HTTPS URL")

        return value