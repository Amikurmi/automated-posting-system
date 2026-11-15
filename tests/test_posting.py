import pytest

from app.platforms.base import BasePlatform, PlatformResult
from app.services.posting_service import PostingService


class SuccessPlatform(BasePlatform):

    async def publish(self, message: str) -> PlatformResult:

        return PlatformResult(
            platform="Success Platform",
            status="success",
            posted_url="https://example.com/post/1",
            public_access=True
        )


class FailedPlatform(BasePlatform):

    async def publish(self, message: str) -> PlatformResult:

        raise Exception("Authentication failed")


@pytest.mark.asyncio
async def test_independent_platform_execution():

    platforms = [
        SuccessPlatform(),
        FailedPlatform(),
        SuccessPlatform()
    ]

    service = PostingService(platforms)

    results = await service.publish_all("Hello https://example.com")

    assert len(results) == 3

    assert results[0].status == "success"
    assert results[1].status == "failed"
    assert results[2].status == "success"