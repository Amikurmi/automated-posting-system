
import httpx
from datetime import datetime, timezone

from app.config import settings
from app.platforms.base import BasePlatform, PlatformResult


class GitHubPlatform(BasePlatform):

    API_URL = "https://api.github.com/graphql"

    async def publish(self, message: str) -> PlatformResult:

        now = datetime.now(timezone.utc)

        try:
            token = settings.github_token
            owner = settings.github_owner
            repo = settings.github_repo

            if not all([token, owner, repo]):
                raise ValueError(
                    "GitHub configuration is incomplete"
                )

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=30.0) as client:

                # 1. Fetch repository ID and discussion categories
                repository_query = """
                query($owner: String!, $name: String!) {
                    repository(owner: $owner, name: $name) {
                        id
                        discussionCategories(first: 25) {
                            nodes {
                                id
                                name
                            }
                        }
                    }
                }
                """

                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json={
                        "query": repository_query,
                        "variables": {
                            "owner": owner,
                            "name": repo,
                        },
                    },
                )

                response.raise_for_status()
                data = response.json()

                if data.get("errors"):
                    raise RuntimeError(str(data["errors"]))

                repository = data["data"]["repository"]

                if not repository:
                    raise RuntimeError("GitHub repository not found")

                repository_id = repository["id"]

                categories = repository[
                    "discussionCategories"
                ]["nodes"]

                if not categories:
                    raise RuntimeError(
                        "No GitHub Discussion category found"
                    )

                # Prefer General category
                category = next(
                    (
                        item for item in categories
                        if item["name"].lower() == "general"
                    ),
                    categories[0],
                )

                category_id = category["id"]

                # 2. Create GitHub Discussion
                mutation = """
                mutation(
                    $repositoryId: ID!,
                    $categoryId: ID!,
                    $title: String!,
                    $body: String!
                ) {
                    createDiscussion(
                        input: {
                            repositoryId: $repositoryId,
                            categoryId: $categoryId,
                            title: $title,
                            body: $body
                        }
                    ) {
                        discussion {
                            url
                            createdAt
                        }
                    }
                }
                """

                response = await client.post(
                    self.API_URL,
                    headers=headers,
                    json={
                        "query": mutation,
                        "variables": {
                            "repositoryId": repository_id,
                            "categoryId": category_id,
                            "title": "Automated Social Media Update",
                            "body": message,
                        },
                    },
                )

                response.raise_for_status()
                result = response.json()

                if result.get("errors"):
                    raise RuntimeError(str(result["errors"]))

                discussion = result["data"][
                    "createDiscussion"
                ]["discussion"]

                created_at = datetime.fromisoformat(
                    discussion["createdAt"].replace(
                        "Z", "+00:00"
                    )
                )

                return PlatformResult(
                    platform="GitHub",
                    status="success",
                    posted_url=discussion["url"],
                    public_access=True,
                    date=created_at.strftime("%Y-%m-%d"),
                    time=created_at.strftime("%H:%M:%S"),
                    error=None,
                )

        except Exception as e:

            return PlatformResult(
                platform="GitHub",
                status="failed",
                posted_url=None,
                public_access=False,
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
                error=str(e),
            )
