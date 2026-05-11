"""Run: python test_llm.py — confirms your LLM key and connection work."""
from llm import get_llm

llm = get_llm()
response = llm.invoke("Reply with exactly: LLM connection successful.")
print(response.content)
