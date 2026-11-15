
import httpx

from datetime import datetime, timezone

from app.config import settings

from app.platforms.base import (
    BasePlatform,
    PlatformResult
)


class BlueskyPlatform(BasePlatform):

    async def publish(self, message: str) -> PlatformResult:

        if not settings.bluesky_handle:
            raise RuntimeError(
                "Bluesky handle is not configured"
            )

        if not settings.bluesky_app_password:
            raise RuntimeError(
                "Bluesky app password is not configured"
            )

        base_url = settings.bluesky_base_url.rstrip("/")

        async with httpx.AsyncClient(timeout=30.0) as client:

            # Step 1: Authenticate with Bluesky

            session_response = await client.post(
                f"{base_url}/xrpc/com.atproto.server.createSession",
                json={
                    "identifier": settings.bluesky_handle,
                    "password": settings.bluesky_app_password
                }
            )

            if session_response.is_error:
                raise RuntimeError(
                    f"Bluesky authentication failed: "
                    f"{session_response.status_code}"
                )

            session = session_response.json()

            access_token = session["accessJwt"]
            user_did = session["did"]

            # Step 2: Prepare post record

            created_at = (
                datetime.now(timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z")
            )

            record = {
                "$type": "app.bsky.feed.post",
                "text": message,
                "createdAt": created_at
            }

            # Step 3: Publish post

            headers = {
                "Authorization": f"Bearer {access_token}"
            }

            payload = {
                "repo": user_did,
                "collection": "app.bsky.feed.post",
                "record": record
            }

            post_response = await client.post(
                f"{base_url}/xrpc/com.atproto.repo.createRecord",
                headers=headers,
                json=payload
            )

            if post_response.is_error:
                try:
                    error_data = post_response.json()
                    error_message = error_data.get(
                        "message",
                        error_data.get(
                            "error",
                            "Bluesky publishing failed"
                        )
                    )
                except ValueError:
                    error_message = "Bluesky publishing failed"

                raise RuntimeError(
                    f"Bluesky API error "
                    f"({post_response.status_code}): "
                    f"{error_message}"
                )

            data = post_response.json()

        # Step 4: Extract actual post URI

        post_uri = data.get("uri")

        if not post_uri:
            raise RuntimeError(
                "Bluesky did not return a post URI"
            )

        # AT URI contains the repository and record key.
        record_key = post_uri.rsplit("/", 1)[-1]

        handle = session.get(
            "handle",
            settings.bluesky_handle
        )

        post_url = (
            f"https://bsky.app/profile/{handle}/post/{record_key}"
        )

        # Step 5: Return standardized result

        created_datetime = datetime.fromisoformat(
            created_at.replace("Z", "+00:00")
        )

        return PlatformResult(
            platform="Bluesky",
            status="success",
            posted_url=post_url,
            public_access=True,
            date=created_datetime.date().isoformat(),
            time=created_datetime.time().replace(
                tzinfo=None
            ).isoformat(timespec="seconds"),
            error=None
        )
