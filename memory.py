import hashlib
from typing import List, Optional
from supabase import create_client, Client
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from config import config


class MemoryStore:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.vector_store: Optional[SupabaseVectorStore] = None
        self._init_supabase()

    def _init_supabase(self):
        """Initialize Supabase client and vector store."""
        supabase_url = config.SUPABASE_URL
        supabase_key = config.SUPABASE_KEY

        if not supabase_url or not supabase_key:
            print("⚠️  Supabase not configured — memory disabled")
            return

        self.supabase = create_client(supabase_url, supabase_key)
        embeddings = OpenAIEmbeddings(
            openai_api_key=config.GROQ_API_KEY,
            openai_api_base="https://api.groq.com/openai/v1",
            model="text-embedding-3-small",
        )
        self.vector_store = SupabaseVectorStore(
            client=self.supabase,
            embedding=embeddings,
            table_name="pr_reviews",
            query_name="match_pr_reviews",
        )

    def store_review(self, repo: str, pr_number: int, diff: str, review: str) -> str:
        """Store a review in memory with embedding."""
        if not self.vector_store:
            return ""

        # Create a unique ID for this review
        review_id = hashlib.md5(f"{repo}/{pr_number}".encode()).hexdigest()
        metadata = {
            "repo": repo,
            "pr_number": pr_number,
            "review_id": review_id,
            "diff_hash": hashlib.md5(diff.encode()).hexdigest(),
        }

        # Store both diff and review as separate documents
        self.vector_store.add_texts(
            texts=[diff, review],
            metadatas=[metadata, metadata],
            ids=[f"{review_id}_diff", f"{review_id}_review"],
        )
        return review_id

    def find_similar_reviews(self, diff: str, k: int = 3) -> List[str]:
        """Find similar past reviews based on diff similarity."""
        if not self.vector_store:
            return []

        results = self.vector_store.similarity_search(diff, k=k)
        similar_reviews = []
        for doc in results:
            if doc.metadata.get("review_id", "").endswith("_review"):
                similar_reviews.append(doc.page_content)
        return similar_reviews

    def get_context_for_review(self, diff: str) -> str:
        """Retrieve similar past reviews to provide context."""
        similar = self.find_similar_reviews(diff)
        if not similar:
            return ""

        context = "## Similar Past Reviews\n"
        for i, review in enumerate(similar[:2], 1):
            context += f"**Review {i}:**\n{review[:500]}...\n\n"
        return context


# Global instance
memory = MemoryStore()
