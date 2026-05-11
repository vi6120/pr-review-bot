from langchain_core.language_models import BaseChatModel
from config import config


def get_llm() -> BaseChatModel:
    if config.LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=config.LLM_MODEL or "gemini-1.5-flash",
            google_api_key=config.GOOGLE_API_KEY,
        )

    # Default: Groq
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=config.LLM_MODEL,
        api_key=config.GROQ_API_KEY,
        temperature=0,
    )
