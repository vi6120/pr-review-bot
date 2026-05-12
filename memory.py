import hashlib
import logging
from typing import Optional
from supabase import create_client, Client
from config import config

logger = logging.getLogger(__name__)


class MemoryStore:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self._init_supabase()

    def _init_supabase(self):
        if not config.SUPABASE_URL or not config.SUPABASE_KEY:
            logger.warning("Supabase not configured — memory disabled")
            return
        try:
            self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            logger.info("Supabase memory store initialized")
        except Exception as e:
            logger.warning(f"Memory initialization failed: {e}")
            self.supabase = None

    def store_review(self, repo: str, pr_number: int, diff: str, review: str) -> None:
        if not self.supabase:
            return
        try:
            self.supabase.table("pr_reviews").upsert({
                "id": hashlib.md5(f"{repo}/{pr_number}".encode()).hexdigest(),
                "repo": repo,
                "pr_number": pr_number,
                "diff": diff[:5000],   # cap stored diff size
                "review": review[:5000],
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to store review: {e}")

    def get_context_for_review(self, repo: str) -> str:
        """Retrieve the last 2 reviews from the same repo as context."""
        if not self.supabase:
            return ""
        try:
            result = (
                self.supabase.table("pr_reviews")
                .select("review")
                .eq("repo", repo)
                .order("created_at", desc=True)
                .limit(2)
                .execute()
            )
            reviews = [r["review"] for r in result.data if r.get("review")]
            if not reviews:
                return ""
            context = "## Past Reviews From This Repo\n"
            for i, r in enumerate(reviews, 1):
                context += f"**Review {i}:**\n{r[:500]}...\n\n"
            return context
        except Exception as e:
            logger.warning(f"Failed to fetch memory context: {e}")
            return ""


memory = MemoryStore()
