
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    mastodon_base_url: str = "https://mastodon.social"
    mastodon_access_token: str | None = None

    bluesky_base_url: str = "https://bsky.social"
    bluesky_handle: str | None = None
    bluesky_app_password: str | None = None

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    discord_webhook_url: str | None = None

    github_token: str | None = None
    github_owner: str | None = None
    github_repo: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )


# Initialize settings
settings = Settings()

