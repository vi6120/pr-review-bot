import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from github_client import (
    verify_signature, get_pr_diff, get_pr_files_content,
    get_pr_comment_thread, post_pr_comment
)
from github_app import get_installation_token
from agents import run_review
from chat_agent import run_chat
from memory import memory

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
    
    # Store in memory for future context
    try:
        memory.store_review(repo, pr_number, diff, comment)
        logger.info(f"Stored review in memory for PR #{pr_number}")
    except Exception as e:
        logger.warning(f"Failed to store review in memory: {e}")


@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    payload_bytes = await request.body()

    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event = request.headers.get("X-GitHub-Event", "")

    # Handle PR opened/synchronize — run full review
    if event == "pull_request" and payload.get("action") in ("opened", "synchronize"):
        installation_id = payload["installation"]["id"]
        background_tasks.add_task(process_pr, payload, installation_id)
        logger.info(f"Queued review for PR #{payload['pull_request']['number']}")

    # Handle PR comments — respond to @mentions
    if event == "issue_comment" and payload.get("action") == "created":
        if payload["issue"].get("pull_request"):  # only on PRs, not issues
            installation_id = payload["installation"]["id"]
            background_tasks.add_task(process_comment, payload, installation_id)

    return {"status": "ok"}  # Always return 200 immediately


async def process_comment(payload: dict, installation_id: int) -> None:
    """Background task — handles @pr-review-bot mentions in PR comments."""
    repo = payload["repository"]["full_name"]
    comment_body = payload["comment"]["body"]
    commenter = payload["comment"]["user"]["login"]
    pr_number = payload["issue"]["number"]

    # Ignore comments from the bot itself to prevent loops
    if commenter == "pr-review-bot[bot]":
        return

    # Only respond to @pr-review-bot mentions
    if "@pr-review-bot" not in comment_body:
        return

    logger.info(f"Chat request on PR #{pr_number} from {commenter}")

    token = get_installation_token(installation_id)

    # Strip the @mention to get the actual question
    question = comment_body.replace("@pr-review-bot", "").strip()

    # Fetch all context in parallel
    diff = get_pr_diff(repo, pr_number, token)
    files_content = get_pr_files_content(repo, pr_number, token)
    thread = get_pr_comment_thread(repo, pr_number, token)

    reply = run_chat(question, diff, files_content, thread)
    post_pr_comment(repo, pr_number, token, f"@{commenter} {reply}")
    logger.info(f"Posted chat reply on PR #{pr_number}")


@app.get("/health")
async def health():
    return {"status": "healthy"}
