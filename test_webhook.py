"""
Simulates a GitHub PR webhook event locally.
Run the server first: uvicorn webhook:app --reload --port 8000
Then in another terminal: python test_webhook.py
"""
import httpx

PAYLOAD = {
    "action": "opened",
    "pull_request": {
        "number": 1,
        "title": "Test PR",
    },
    "repository": {
        "full_name": "test-owner/test-repo",
    },
}

response = httpx.post(
    "http://localhost:8000/webhook",
    json=PAYLOAD,
    headers={"X-GitHub-Event": "pull_request"},
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
