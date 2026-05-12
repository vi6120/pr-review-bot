import asyncio
import logging
import time
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from github_client import (
    verify_signature, get_pr_diff, get_pr_files_content,
    get_pr_comment_thread, post_pr_comment
)
from github_app import get_installation_token
from agents import run_review
from chat_agent import run_chat
from memory import memory
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Rate limiting: tracks last review time per repo ---
_rate_limit_store: dict = defaultdict(float)


def is_rate_limited(repo: str) -> bool:
    now = time.time()
    window = 3600 / config.RATE_LIMIT_PER_HOUR  # seconds between allowed reviews
    last = _rate_limit_store[repo]
    if now - last < window:
        return True
    _rate_limit_store[repo] = now
    return False


# --- PR review pipeline ---

async def process_pr(payload: dict, installation_id: int) -> None:
    repo = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
    pr_title = payload["pull_request"]["title"]
    logger.info(f"Processing PR #{pr_number}: {pr_title} in {repo}")

    if is_rate_limited(repo):
        logger.warning(f"Rate limited: skipping PR #{pr_number} in {repo}")
        return

    try:
        await asyncio.wait_for(_run_review(repo, pr_number, installation_id), timeout=config.REVIEW_TIMEOUT)
    except asyncio.TimeoutError:
        logger.error(f"Review timed out for PR #{pr_number} in {repo}")
        token = get_installation_token(installation_id)
        post_pr_comment(repo, pr_number, token,
            "⚠️ Review timed out — the PR may be too large. Try breaking it into smaller PRs.")
    except Exception as e:
        logger.error(f"Review failed for PR #{pr_number}: {e}")


async def _run_review(repo: str, pr_number: int, installation_id: int) -> None:
    token = get_installation_token(installation_id)
    diff = get_pr_diff(repo, pr_number, token)

    # PR size guard
    if len(diff) > config.MAX_DIFF_SIZE:
        logger.warning(f"PR #{pr_number} diff too large ({len(diff)} chars) — skipping")
        post_pr_comment(repo, pr_number, token,
            f"⚠️ This PR is too large to review automatically ({len(diff):,} chars). "
            "Please break it into smaller PRs for a full review.")
        return

    files_content = get_pr_files_content(repo, pr_number, token)
    logger.info(f"Fetched diff for PR #{pr_number} ({len(diff)} chars)")

    comment = run_review(diff, files_content, repo)
    post_pr_comment(repo, pr_number, token, comment)
    logger.info(f"Posted review comment on PR #{pr_number}")

    try:
        memory.store_review(repo, pr_number, diff, comment)
        logger.info(f"Stored review in memory for PR #{pr_number}")
    except Exception as e:
        logger.warning(f"Failed to store review in memory: {e}")


# --- Chat pipeline ---

async def process_comment(payload: dict, installation_id: int) -> None:
    repo = payload["repository"]["full_name"]
    comment_body = payload["comment"]["body"]
    commenter = payload["comment"]["user"]["login"]
    pr_number = payload["issue"]["number"]

    if commenter == config.GITHUB_BOT_USERNAME:
        return

    mention = f"@{config.GITHUB_BOT_USERNAME}"
    if mention not in comment_body:
        return

    logger.info(f"Chat request on PR #{pr_number} from {commenter}")

    try:
        await asyncio.wait_for(
            _run_chat(repo, pr_number, installation_id, commenter, comment_body, mention),
            timeout=config.REVIEW_TIMEOUT
        )
    except asyncio.TimeoutError:
        logger.error(f"Chat timed out for PR #{pr_number}")
    except Exception as e:
        logger.error(f"Chat failed for PR #{pr_number}: {e}")


async def _run_chat(repo: str, pr_number: int, installation_id: int,
                    commenter: str, comment_body: str, mention: str) -> None:
    token = get_installation_token(installation_id)
    question = comment_body.replace(mention, "").strip()
    diff = get_pr_diff(repo, pr_number, token)
    files_content = get_pr_files_content(repo, pr_number, token)
    thread = get_pr_comment_thread(repo, pr_number, token)
    reply = run_chat(question, diff, files_content, thread)
    post_pr_comment(repo, pr_number, token, f"@{commenter} {reply}")
    logger.info(f"Posted chat reply on PR #{pr_number}")


# --- Webhook handler ---

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    payload_bytes = await request.body()

    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event = request.headers.get("X-GitHub-Event", "")

    if event == "pull_request" and payload.get("action") in ("opened", "synchronize"):
        installation_id = payload["installation"]["id"]
        background_tasks.add_task(process_pr, payload, installation_id)
        logger.info(f"Queued review for PR #{payload['pull_request']['number']}")

    if event == "issue_comment" and payload.get("action") == "created":
        if payload["issue"].get("pull_request"):
            installation_id = payload["installation"]["id"]
            background_tasks.add_task(process_comment, payload, installation_id)

    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/ping")
async def ping():
    """Keep-alive endpoint — used by UptimeRobot to prevent Railway sleep."""
    return {"status": "alive"}
