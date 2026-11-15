
import httpx

from datetime import datetime, timezone

from app.config import settings

from app.platforms.base import (
    BasePlatform,
    PlatformResult
)


class TelegramPlatform(BasePlatform):

    async def publish(self, message: str) -> PlatformResult:

        if not settings.telegram_bot_token:
            raise RuntimeError(
                "Telegram bot token is not configured"
            )

        if not settings.telegram_chat_id:
            raise RuntimeError(
                "Telegram channel ID is not configured"
            )

        api_url = (
            "https://api.telegram.org/"
            f"bot{settings.telegram_bot_token}/sendMessage"
        )

        payload = {
            "chat_id": settings.telegram_chat_id,
            "text": message,
            "disable_notification": False
        }

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.post(
                api_url,
                json=payload
            )


            if response.is_error:

                try:
                    error_data = response.json()

                    error_message = error_data.get(
                        "description",
                        "Unknown Telegram API error"
                    )

                except ValueError:
                    error_message = response.text

                raise RuntimeError(
                    f"Telegram API error ({response.status_code}): "
                    f"{error_message}"
                )


            data = response.json()

            if not data.get("ok"):
                raise RuntimeError(
                    data.get(
                        "description",
                        "Telegram publishing failed"
                    )
                )

            result = data["result"]

        # Extract Telegram message information
        message_id = result["message_id"]
        chat = result["chat"]

        chat_username = chat.get("username")

        # Construct public URL only for public channels
        if chat_username:
            posted_url = (
                f"https://t.me/{chat_username}/{message_id}"
            )
            public_access = True
        else:
            posted_url = None
            public_access = False

        # Telegram returns Unix timestamp
        created_datetime = datetime.fromtimestamp(
            result["date"],
            tz=timezone.utc
        )

        return PlatformResult(
            platform="Telegram",
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=created_datetime.date().isoformat(),
            time=created_datetime.time().replace(
                tzinfo=None
            ).isoformat(timespec="seconds"),
            error=None
        )
