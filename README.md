# PR Review Bot

An AI-powered GitHub App that automatically reviews every Pull Request for bugs, security vulnerabilities, and performance issues.

[![Install App](https://img.shields.io/badge/GitHub%20App-Install%20Free-blue?logo=github)](https://github.com/apps/pullrequest-review-bot)
![Free](https://img.shields.io/badge/cost-free-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What it does

- **Automatic reviews** — analyzes every PR when opened or updated
- **3 parallel AI agents** — code quality, security, and performance analyzed simultaneously
- **Interactive chat** — ask questions by mentioning `@pullrequest-review-bot[bot]` in comments
- **Learning memory** — gets smarter over time using past reviews from your repo as context
- **Fast** — returns results in under 30 seconds for most PRs
- **Secure** — HMAC signature verification, rate limiting, and timeout protection

---

## Example Review

When you open a PR, the bot posts a comment like this:

> **Code Review Summary**
> 
> This PR requires attention for security and performance issues.
> 
> ### Security Review
> - **Line 23 in `auth/login.py`**: SQL query built with string concatenation — vulnerable to SQL injection. Use parameterized queries instead.
> - **Line 45**: Hardcoded API key detected. Move to environment variables.
> 
> ### Performance Review  
> - **Line 67 in `api/users.py`**: N+1 query inside loop. Fetch all users in a single query before the loop.
> - **Line 102**: Large commented-out code block (50+ lines) should be removed to improve readability.
> 
> ### Code Quality Review
> - Overall structure is clean and follows best practices
> - Consider extracting validation logic from `validate_user()` into smaller helper functions
> - Good use of type hints throughout

---

## How to Install

1. **Click [Install App](https://github.com/apps/pullrequest-review-bot)**
2. Choose your **personal account** or **organization**
3. Select **which repositories** to grant access to (or choose "All repositories")
4. Click **Install**
5. Open a PR in any enabled repo — the bot reviews it automatically within seconds

That's it! No configuration files, no setup, no API keys needed.

---

## Ask the Bot Questions

The bot isn't just a one-time reviewer — you can have a conversation with it. Mention `@pullrequest-review-bot[bot]` in any PR comment:

**Examples:**
```
@pullrequest-review-bot[bot] why is line 23 a security risk?

@pullrequest-review-bot[bot] can you suggest a fix for the N+1 query?

@pullrequest-review-bot[bot] is this approach thread-safe?

@pullrequest-review-bot[bot] what does the validate_user function do?
```

The bot has full context of:
- The entire PR diff
- Full contents of all changed files
- The complete comment thread history

It remembers the conversation, so you can ask follow-up questions naturally.

---

## Architecture

```
GitHub PR Event
      │
      ▼
   Webhook
      │
      ├── Signature verification
      ├── Rate limiting (10/hour per repo)
      ├── PR size check (skip if > 50KB)
      └── Background task
              │
              ▼
      LangGraph Pipeline
      ┌──────────────┐
      │   fan_out    │
      └──┬────┬────┬─┘
         │    │    │
         ▼    ▼    ▼
      Code Security Performance
      Agent  Agent   Agent
         │    │    │
         └────┴────┘
              │
              ▼
        Summarizer
              │
     ┌────────┴────────┐
     ▼                 ▼
Post to GitHub    Store in Memory
                  (Supabase)
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Server** | FastAPI + Railway | Webhook receiver, always-on hosting |
| **AI Framework** | LangGraph | Multi-agent orchestration |
| **LLM** | LLaMA 3.3 70B (Groq) | Code analysis and chat |
| **GitHub Integration** | PyGitHub + GitHub App | Authentication, API calls |
| **Memory** | Supabase (Postgres) | Store past reviews per repo |
| **Keep-alive** | UptimeRobot | Prevent Railway sleep |

---

## Privacy & Security

- ✅ Only reads code from repos you **explicitly grant access** to
- ✅ Review data stored **per-repository** to improve future reviews
- ✅ No code shared with third parties beyond the LLM provider (Groq)
- ✅ All webhooks verified with **HMAC signatures**
- ✅ **Rate limited** to prevent abuse (10 reviews per repo per hour)
- ✅ **Timeout protection** — reviews that take longer than 2 minutes are cancelled
- ✅ **PR size guard** — skips PRs larger than 50KB with a helpful message

---

## Features

### Automatic PR Reviews
- Triggered on every `pull_request` opened or synchronized event
- Three specialized agents run in parallel:
  - **Code Quality Agent** — logic errors, readability, best practices, commented-out code
  - **Security Agent** — SQL injection, XSS, hardcoded secrets, insecure dependencies
  - **Performance Agent** — N+1 queries, inefficient loops, memory leaks, blocking operations
- Summarizer combines findings into one clean markdown comment

### Interactive Chat
- Multi-turn conversations with full context
- Understands the entire PR, not just the diff
- Can answer questions about existing code, not just changes
- Remembers the conversation thread

### Learning Memory
- Every review stored in Supabase
- Future reviews on the same repo retrieve past reviews as context
- Bot learns your codebase patterns over time

### Production-Grade Safeguards
- **Rate limiting** — prevents API quota exhaustion
- **Timeouts** — no runaway background tasks
- **Size limits** — gracefully handles massive PRs
- **Error handling** — failures don't crash the bot
- **Structured logging** — easy debugging

---

## Costs (All Free Tier)

| Service | Free Limit | Our Usage | Cost |
|---------|------------|-----------|------|
| **Groq** | 14,400 requests/day | ~4 requests per PR | $0 |
| **Railway** | $5 credit/month | ~$0.50/month at low volume | $0 |
| **Supabase** | 500MB database | ~2KB per review | $0 |
| **UptimeRobot** | 50 monitors | 1 monitor | $0 |
| **GitHub App** | Unlimited | Unlimited | $0 |

**Total: $0/month** for personal use or small teams.

---

## Self-Hosting

Want to run your own instance? Here's how:

### Prerequisites
- Python 3.12+
- GitHub account
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Supabase account (free at [supabase.com](https://supabase.com))

### Setup

1. **Clone the repo**
```bash
git clone https://github.com/vi6120/pr-review-bot.git
cd pr-review-bot
```

2. **Install dependencies**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and fill in:
# - GROQ_API_KEY (from console.groq.com)
# - GITHUB_APP_ID (from your GitHub App)
# - GITHUB_PRIVATE_KEY_PATH (path to your .pem file)
# - GITHUB_WEBHOOK_SECRET (generate with: openssl rand -hex 32)
# - SUPABASE_URL (from your Supabase project)
# - SUPABASE_KEY (from your Supabase project)
```

4. **Set up Supabase**
```bash
# Run the SQL in setup_supabase.py in your Supabase SQL editor
python setup_supabase.py
```

5. **Create a GitHub App**
- Go to [github.com/settings/apps/new](https://github.com/settings/apps/new)
- Fill in:
  - **App name**: `your-bot-name`
  - **Homepage URL**: `https://github.com/your-username/pr-review-bot`
  - **Webhook URL**: `https://your-domain.com/webhook` (use ngrok for local dev)
  - **Webhook secret**: (paste the value from your `.env`)
- **Permissions**:
  - Pull requests: Read & Write
  - Contents: Read
  - Issues: Read & Write
- **Subscribe to events**: Pull request, Issue comment
- Generate a private key and save it as `private-key.pem`

6. **Run locally**
```bash
uvicorn webhook:app --reload --port 8000
```

7. **Deploy to Railway** (recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

8. **Set up keep-alive** (optional, prevents Railway sleep)
- Sign up at [uptimerobot.com](https://uptimerobot.com)
- Add HTTP(s) monitor pointing to `https://your-app.railway.app/ping`
- Set interval to 5 minutes

---

## Configuration

Optional environment variables for tuning:

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_PER_HOUR` | `10` | Max reviews per repo per hour |
| `MAX_DIFF_SIZE` | `50000` | Skip PRs with diffs larger than this (chars) |
| `REVIEW_TIMEOUT` | `120` | Timeout for review tasks (seconds) |
| `GITHUB_BOT_USERNAME` | `pullrequest-review-bot[bot]` | Bot's GitHub username |
| `LLM_PROVIDER` | `groq` | LLM provider (`groq` or `gemini`) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Model name |

---

## Contributing

Contributions are welcome! Here's how:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Ideas for contributions:**
- Add support for more LLM providers (Anthropic, OpenAI)
- Implement review re-trigger command (`@bot re-review`)
- Add per-user analytics dashboard
- Support for monorepo path filtering
- Integration with Slack/Discord for notifications

---

## License

MIT License — free for personal and commercial use.

See [LICENSE](LICENSE) for details.

---

## Acknowledgments

Built by **Vikas Ramaswamy** ([@vi6120](https://github.com/vi6120))

Powered by:
- [Groq](https://groq.com) — blazing fast LLM inference
- [LangChain](https://langchain.com) & [LangGraph](https://langchain-ai.github.io/langgraph/) — agent orchestration
- [Railway](https://railway.app) — deployment platform
- [Supabase](https://supabase.com) — database and storage

---

## Support

- **Issues**: [GitHub Issues](https://github.com/vi6120/pr-review-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vi6120/pr-review-bot/discussions)

---

## Roadmap

- [ ] GitHub Marketplace listing
- [ ] Sentry error tracking integration
- [ ] Review re-trigger command
- [ ] Support for review comments on specific lines
- [ ] Configurable review rules per repo
- [ ] Integration with CI/CD pipelines
- [ ] Multi-language support for comments
- [ ] Analytics dashboard

---

## Star History

If you find this useful, please star the repo!

[![Star History Chart](https://api.star-history.com/svg?repos=vi6120/pr-review-bot&type=Date)](https://star-history.com/#vi6120/pr-review-bot&Date)

---

**[Install Now](https://github.com/apps/pullrequest-review-bot)** • **[View Source](https://github.com/vi6120/pr-review-bot)** • **[Report Bug](https://github.com/vi6120/pr-review-bot/issues)**
