import hmac
import hashlib
import base64
from typing import List
from github import Github, Auth
from config import config


def verify_signature(payload: bytes, signature: str) -> bool:
    if not config.GITHUB_WEBHOOK_SECRET:
        return True
    expected = "sha256=" + hmac.new(
        config.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def get_pr_diff(repo_full_name: str, pr_number: int, token: str) -> str:
    g = Github(auth=Auth.Token(token))
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    diff_parts = []
    for f in pr.get_files():
        diff_parts.append(f"### {f.filename}\n```\n{f.patch or ''}\n```")
    return "\n\n".join(diff_parts)


def get_pr_files_content(repo_full_name: str, pr_number: int, token: str) -> str:
    """Fetch full file contents for all files changed in the PR."""
    g = Github(auth=Auth.Token(token))
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    parts = []
    for f in pr.get_files():
        try:
            content = repo.get_contents(f.filename, ref=pr.head.sha)
            decoded = base64.b64decode(content.content).decode("utf-8", errors="replace")
            parts.append(f"### {f.filename}\n```\n{decoded}\n```")
        except Exception:
            parts.append(f"### {f.filename}\n(could not fetch content)")
    return "\n\n".join(parts)


def get_pr_comment_thread(repo_full_name: str, pr_number: int, token: str) -> List[dict]:
    """Fetch all issue comments on a PR as a list of {author, body} dicts."""
    g = Github(auth=Auth.Token(token))
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    return [
        {"author": c.user.login, "body": c.body}
        for c in pr.get_issue_comments()
    ]


def post_pr_comment(repo_full_name: str, pr_number: int, token: str, body: str) -> None:
    g = Github(auth=Auth.Token(token))
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)
