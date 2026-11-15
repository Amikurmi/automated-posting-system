import httpx

from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform, PlatformResult


class MastodonPlatform(BasePlatform):

    async def publish(self, message: str) -> PlatformResult:

        if not settings.mastodon_access_token:
            raise RuntimeError(
                "Mastodon access token is not configured"
            )

        base_url = settings.mastodon_base_url.rstrip("/")

        api_url = f"{base_url}/api/v1/statuses"

        headers = {
            "Authorization": (
                f"Bearer {settings.mastodon_access_token}"
            )
        }

        payload = {
            "status": message,
            "visibility": "public"
        }

        async with httpx.AsyncClient(timeout=20.0) as client:

            response = await client.post(
                api_url,
                headers=headers,
                data=payload
            )

            if response.is_error:
                try:
                    error_data = response.json()
                    error_message = error_data.get(
                        "error",
                        "Mastodon API request failed"
                    )
                except ValueError:
                    error_message = "Mastodon API request failed"

                raise RuntimeError(
                    f"Mastodon API error ({response.status_code}): "
                    f"{error_message}"
                )

            data = response.json()

        post_url = data.get("url")
        visibility = data.get("visibility")
        created_at = data.get("created_at")

        if not post_url or not created_at:
            raise RuntimeError(
                "Mastodon returned an incomplete post response"
            )

        created_datetime = datetime.fromisoformat(
            created_at.replace("Z", "+00:00")
        )

        return PlatformResult(
            platform="Mastodon",
            status="success",
            posted_url=post_url,
            public_access=(
                visibility == "public" and bool(post_url)
            ),
            date=created_datetime.date().isoformat(),
            time=created_datetime.time().replace(
                tzinfo=None
            ).isoformat(timespec="seconds"),
            error=None
        )