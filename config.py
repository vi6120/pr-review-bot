from dotenv import load_dotenv
import os
import base64
import tempfile

load_dotenv()

class Config:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    GITHUB_APP_ID: str = os.getenv("GITHUB_APP_ID", "")
    GITHUB_PRIVATE_KEY_PATH: str = os.getenv("GITHUB_PRIVATE_KEY_PATH", "")
    GITHUB_BOT_USERNAME: str = os.getenv("GITHUB_BOT_USERNAME", "pr-review-bot[bot]")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    # Rate limiting: max reviews per repo per hour
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "10"))

    # PR size guard: skip review if diff exceeds this character count
    MAX_DIFF_SIZE: int = int(os.getenv("MAX_DIFF_SIZE", "50000"))

    # Timeout in seconds for background review tasks
    REVIEW_TIMEOUT: int = int(os.getenv("REVIEW_TIMEOUT", "120"))

    def __init__(self):
        encoded_key = os.getenv("GITHUB_PRIVATE_KEY", "")
        if encoded_key and not self.GITHUB_PRIVATE_KEY_PATH:
            with tempfile.NamedTemporaryFile(mode="wb", suffix=".pem", delete=False) as f:
                f.write(base64.b64decode(encoded_key))
                self.GITHUB_PRIVATE_KEY_PATH = f.name

config = Config()
