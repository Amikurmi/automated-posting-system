from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel


class PlatformResult(BaseModel):

    platform: str

    status: Literal["success", "failed"]

    posted_url: str | None = None

    public_access: bool = False

    date: str | None = None

    time: str | None = None

    error: str | None = None


class BasePlatform(ABC):

    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        """
        Publish message to a third-party platform.
        """
        pass