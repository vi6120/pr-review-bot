from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from llm import get_llm

llm = get_llm()


# --- State ---

class ReviewState(TypedDict):
    diff: str
    reviewer_output: str
    security_output: str
    performance_output: str
    final_comment: str


# --- Agents ---

def reviewer_agent(state: ReviewState) -> dict:
    response = llm.invoke([HumanMessage(content=(
        "You are a code reviewer. Review the following PR diff for code quality, "
        "logic errors, readability, and best practices. Be concise and specific.\n\n"
        f"{state['diff']}"
    ))])
    return {"reviewer_output": response.content}


def security_agent(state: ReviewState) -> dict:
    response = llm.invoke([HumanMessage(content=(
        "You are a security expert. Review the following PR diff for security vulnerabilities "
        "such as injection risks, exposed secrets, insecure dependencies, or auth issues. "
        "Be concise. If no issues found, say so.\n\n"
        f"{state['diff']}"
    ))])
    return {"security_output": response.content}


def performance_agent(state: ReviewState) -> dict:
    response = llm.invoke([HumanMessage(content=(
        "You are a performance engineer. Review the following PR diff for performance issues "
        "such as inefficient loops, unnecessary DB calls, memory leaks, or blocking operations. "
        "Be concise. If no issues found, say so.\n\n"
        f"{state['diff']}"
    ))])
    return {"performance_output": response.content}


def fan_out(state: ReviewState) -> dict:
    """No-op entry node — triggers parallel execution of all 3 agents."""
    return {}


def summarizer_agent(state: ReviewState) -> dict:
    response = llm.invoke([HumanMessage(content=(
        "You are a senior engineer summarizing a PR review. "
        "Combine the three reviews below into a single clean GitHub PR comment using markdown. "
        "Start with a one-line overall summary, then use sections for each area.\n\n"
        f"## Code Review\n{state['reviewer_output']}\n\n"
        f"## Security Review\n{state['security_output']}\n\n"
        f"## Performance Review\n{state['performance_output']}"
    ))])
    return {"final_comment": response.content}


# --- Graph ---

def run_review(diff: str) -> str:
    """Entry point — takes a PR diff, returns the final markdown comment."""
    graph = StateGraph(ReviewState)

    graph.add_node("fan_out", fan_out)
    graph.add_node("reviewer", reviewer_agent)
    graph.add_node("security", security_agent)
    graph.add_node("performance", performance_agent)
    graph.add_node("summarizer", summarizer_agent)

    # Entry fans out to all 3 agents in parallel
    graph.set_entry_point("fan_out")
    graph.add_edge("fan_out", "reviewer")
    graph.add_edge("fan_out", "security")
    graph.add_edge("fan_out", "performance")

    # All 3 agents converge into summarizer
    graph.add_edge("reviewer", "summarizer")
    graph.add_edge("security", "summarizer")
    graph.add_edge("performance", "summarizer")

    graph.add_edge("summarizer", END)

    app = graph.compile()
    result = app.invoke({"diff": diff})
    return result["final_comment"]
