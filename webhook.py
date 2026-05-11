import asyncio
import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from github_client import verify_signature, get_pr_diff, post_pr_comment
from github_app import get_installation_token
from agents import run_review

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


async def process_pr(payload: dict, installation_id: int) -> None:
    """Background task — runs the full agent review pipeline."""
    repo = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
    pr_title = payload["pull_request"]["title"]
    logger.info(f"Processing PR #{pr_number}: {pr_title} in {repo}")

    token = get_installation_token(installation_id)

    diff = get_pr_diff(repo, pr_number, token)
    logger.info(f"Fetched diff for PR #{pr_number} ({len(diff)} chars)")

    comment = run_review(diff)
    post_pr_comment(repo, pr_number, token, comment)
    logger.info(f"Posted review comment on PR #{pr_number}")


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    payload_bytes = await request.body()

    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event = request.headers.get("X-GitHub-Event", "")

    # Only handle PR opened/synchronize events
    if event == "pull_request" and payload.get("action") in ("opened", "synchronize"):
        installation_id = payload["installation"]["id"]
        background_tasks.add_task(process_pr, payload, installation_id)
        logger.info(f"Queued review for PR #{payload['pull_request']['number']}")

    return {"status": "ok"}  # Always return 200 immediately


@app.get("/health")
async def health():
    return {"status": "healthy"}
