import asyncio

from datetime import datetime, timezone

from app.platforms.base import (
    BasePlatform,
    PlatformResult
)


class PostingService:

    def __init__(self, platforms: list[BasePlatform]):

        self.platforms = platforms

    async def publish_to_platform(
        self,
        platform: BasePlatform,
        message: str
    ) -> PlatformResult:

        try:

            result = await platform.publish(message)

            return result

        except Exception as error:

            return PlatformResult(
                platform=platform.__class__.__name__,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error=str(error)
            )

    async def publish_all(
        self,
        message: str
    ) -> list[PlatformResult]:

        tasks = [
            self.publish_to_platform(platform, message)
            for platform in self.platforms
        ]

        results = await asyncio.gather(*tasks)

        return results