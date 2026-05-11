import os
import time
import jwt
import httpx
from config import config


def _generate_jwt() -> str:
    """Generate a short-lived JWT signed with the GitHub App private key."""
    # Read from env variable instead of file
    private_key = os.getenv("GITHUB_PRIVATE_KEY")
    if not private_key:
        raise ValueError("GITHUB_PRIVATE_KEY environment variable is not set")

    now = int(time.time())
    payload = {
        "iat": now - 60,   # issued at (60s back to allow clock drift)
        "exp": now + 540,  # expires in 9 minutes (max is 10)
        "iss": config.GITHUB_APP_ID,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_token(installation_id: int) -> str:
    """Exchange JWT for an installation access token scoped to one repo install."""
    app_jwt = _generate_jwt()
    response = httpx.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
        },
    )
    response.raise_for_status()
    return response.json()["token"]
