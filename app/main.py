
from fastapi import FastAPI

from app.schemas import PostingRequest

from app.platforms.mastodon import MastodonPlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.github import GitHubPlatform

from app.services.posting_service import PostingService


# Initialize FastAPI application
app = FastAPI(
    title="Automated Multi-Platform Posting System",
    description="Automatically publish messages across multiple platforms",
    version="1.0.0"
)


# Configure platforms internally
platforms = [
    MastodonPlatform(),
    BlueskyPlatform(),
    TelegramPlatform(),
    DiscordPlatform(),
    GitHubPlatform()
]

# Initialize posting service
posting_service = PostingService(platforms)


# Home endpoint
@app.get("/")
async def home():

    return {
        "success": True,
        "message": "Automated Posting API is running"
    }


# Main posting endpoint
@app.post("/posting")
async def create_post(request: PostingRequest):

    # Publish message across configured platforms
    results = await posting_service.publish_all(
        request.message
    )

    # Check whether at least one platform succeeded
    successful_posts = sum(
        1 for result in results
        if result.status == "success"
    )

    total_platforms = len(results)

    return {
        "success": successful_posts > 0,
        "total_platforms": total_platforms,
        "successful_posts": successful_posts,
        "failed_posts": total_platforms - successful_posts,
        "results": [
            result.model_dump()
            for result in results
        ]
    }
