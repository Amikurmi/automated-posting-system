# Automated Multi-Platform Posting System

An automated social media posting system built using **Python, FastAPI, and HTTPX**. It allows users to publish a single message across five different platforms through one API endpoint.

## Features

- Publish one message to multiple platforms.
- Supports five platforms:
  - Mastodon
  - Bluesky
  - Telegram
  - Discord
  - GitHub Discussions
- Message validation with a maximum length of 200 characters.
- Validates exactly one HTTP/HTTPS URL in the message.
- Asynchronous publishing using Python `asyncio`.
- Independent error handling for each platform.
- Returns individual publishing results.
- Secure credential management using environment variables.
- Includes automated tests using Pytest.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3 | Backend programming |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Pydantic | Request validation |
| HTTPX | Asynchronous API requests |
| Pydantic Settings | Environment configuration |
| Pytest | Automated testing |

## Supported Platforms

| Platform | Integration |
|---|---|
| Mastodon | REST API |
| Bluesky | AT Protocol API |
| Telegram | Bot API |
| Discord | Webhook API |
| GitHub | GraphQL API (Discussions) |

## Project Structure

```text
automated-posting/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── config.py
│   │
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── mastodon.py
│   │   ├── bluesky.py
│   │   ├── telegram.py
│   │   ├── discord.py
│   │   └── github.py
│   │
│   └── services/
│       └── posting_service.py
│
├── tests/
│   └── test_posting.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Amikurmi/automated-posting-system.git

cd automated-posting-system
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure the following credentials:

```env
# Mastodon
MASTODON_BASE_URL=https://mastodon.social
MASTODON_ACCESS_TOKEN=

# Bluesky
BLUESKY_BASE_URL=https://bsky.social
BLUESKY_HANDLE=
BLUESKY_APP_PASSWORD=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Discord
DISCORD_WEBHOOK_URL=

# GitHub
GITHUB_TOKEN=
GITHUB_OWNER=
GITHUB_REPO=automated-posting-system
```

Use your own valid platform credentials. Never commit the actual `.env` file.

## Run the Application

Start the FastAPI development server:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

Application URL:

http://localhost:4000

Interactive API documentation:

http://localhost:4000/docs

## API Documentation

### Health Check

**GET** `/`

Checks whether the application is running.

### Publish Message

**POST** `/posting`

Request body:

```json
{
  "message": "Hello! Check out my website https://example.com"
}
```

### Response Example

```json
{
  "success": true,
  "total_platforms": 5,
  "successful_posts": 5,
  "failed_posts": 0,
  "results": [
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://example.com/post",
      "public_access": true,
      "date": "2026-11-15",
      "time": "13:36:38",
      "error": null
    }
  ]
}
```

The response contains an individual result for each configured platform.

The top-level `success` field indicates whether at least one platform successfully published the message. Individual platform failures do not prevent other platforms from publishing.

## Validation Rules

- Message must not exceed 200 characters.
- Message must contain exactly one valid HTTP/HTTPS URL.
- Invalid requests are rejected before publishing.

## Testing

Run the automated test suite:

```bash
python -m pytest -v
```

## Security

- API credentials are stored in environment variables.
- `.env` is excluded from Git tracking.
- `.env.example` contains placeholder values only.
- Never commit API tokens, passwords, or webhook URLs.

## Author

Amit Kumar

GitHub: https://github.com/Amikurmi

## License

This project is developed as part of a technical assignment.