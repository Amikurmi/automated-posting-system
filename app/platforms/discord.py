
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform, PlatformResult


class DiscordPlatform(BasePlatform):

    async def publish(self, message: str) -> PlatformResult:

        now = datetime.now(timezone.utc)

        try:
            webhook_url = settings.discord_webhook_url

            if not webhook_url:
                raise ValueError("Discord webhook URL is not configured")

            async with httpx.AsyncClient(timeout=20.0) as client:

                response = await client.post(
                    webhook_url,
                    params={"wait": "true"},
                    json={
                        "content": message,
                        "allowed_mentions": {"parse": []}
                    }
                )

                response.raise_for_status()
                data = response.json()

            message_id = data["id"]
            channel_id = data["channel_id"]
            guild_id = data.get("guild_id")

            posted_url = None

            if guild_id:
                posted_url = (
                    f"https://discord.com/channels/"
                    f"{guild_id}/{channel_id}/{message_id}"
                )

            created_at = datetime.fromisoformat(
                data["timestamp"].replace("Z", "+00:00")
            )

            return PlatformResult(
                platform="Discord",
                status="success",
                posted_url=posted_url,
                public_access=False,
                date=created_at.strftime("%Y-%m-%d"),
                time=created_at.strftime("%H:%M:%S"),
                error=None
            )

        except Exception as e:

            return PlatformResult(
                platform="Discord",
                status="failed",
                posted_url=None,
                public_access=False,
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
                error=str(e)
            )
