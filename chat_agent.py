from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from llm import get_llm

llm = get_llm()

SYSTEM_PROMPT = """You are pr-review-bot, an AI code reviewer embedded in GitHub PRs.
You have access to:
- The full diff of the PR
- The full contents of all changed files
- The entire comment thread on this PR

Answer the developer's question clearly and concisely. Reference specific line numbers,
function names, or file names when relevant. If you previously reviewed this PR, you can
refer back to your earlier comments."""


def run_chat(
    question: str,
    diff: str,
    files_content: str,
    comment_thread: list[dict],
) -> str:
    """Answer a developer's question about a PR with full context."""

    # Build conversation history from comment thread
    history = []
    for comment in comment_thread:
        if comment["author"] == "pr-review-bot[bot]":
            history.append(AIMessage(content=comment["body"]))
        else:
            history.append(HumanMessage(content=f"{comment['author']}: {comment['body']}"))

    context = (
        f"## PR Diff\n{diff}\n\n"
        f"## Full File Contents\n{files_content}"
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Here is the PR context:\n\n{context}"),
        *history,
        HumanMessage(content=question),
    ]

    response = llm.invoke(messages)
    return response.content
