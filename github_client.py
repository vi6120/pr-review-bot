import hmac
import hashlib
from github import Github, Auth
from config import config


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature to ensure request is from GitHub."""
    if not config.GITHUB_WEBHOOK_SECRET:
        return True  # skip verification in local dev
    expected = "sha256=" + hmac.new(
        config.GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def get_pr_diff(repo_full_name: str, pr_number: int, token: str) -> str:
    """Fetch the PR diff as a string."""
    g = Github(auth=Auth.Token(token))
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    files = pr.get_files()
    diff_parts = []
    for f in files:
        diff_parts.append(f"### {f.filename}\n```\n{f.patch or ''}\n```")
    return "\n\n".join(diff_parts)


def post_pr_comment(repo_full_name: str, pr_number: int, token: str, body: str) -> None:
    """Post a comment on the PR."""
    g = Github(auth=Auth.Token(token))
    repo = g.get_repo(repo_full_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)
