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
    MEM0_API_KEY: str = os.getenv("MEM0_API_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Which LLM provider to use: "groq" or "gemini"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")  # groq default

    def __init__(self):
        # Handle base64 encoded private key from Railway
        encoded_key = os.getenv("GITHUB_PRIVATE_KEY", "")
        if encoded_key and not self.GITHUB_PRIVATE_KEY_PATH:
            # Decode and write to temp file
            with tempfile.NamedTemporaryFile(mode="wb", suffix=".pem", delete=False) as f:
                f.write(base64.b64decode(encoded_key))
                self.GITHUB_PRIVATE_KEY_PATH = f.name

config = Config()
