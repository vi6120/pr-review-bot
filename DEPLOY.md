# Deployment instructions for Fly.io

## 1. Install Fly CLI
```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

## 2. Sign up & login
```bash
flyctl auth signup  # or flyctl auth login if you have an account
```

## 3. Create the app
```bash
flyctl launch --no-deploy
# Answer prompts:
# - App name: pr-review-bot (or auto-generated)
# - Region: iad (Virginia) or choose closest
# - Yes to Postgres? No (we use Supabase)
# - Yes to deploy? No (we'll set secrets first)
```

## 4. Set secrets (CRITICAL)
```bash
# Copy your .env values (never commit these!)
flyctl secrets set \
  GROQ_API_KEY="your_groq_key" \
  GITHUB_WEBHOOK_SECRET="your_webhook_secret" \
  GITHUB_APP_ID="3677095" \
  SUPABASE_URL="https://gcfhrudsiuzocvnqgccc.supabase.co" \
  SUPABASE_KEY="your_supabase_key"
```

## 5. Upload private key
```bash
flyctl ssh sftp shell
# Inside SFTP shell:
put pullrequest-review-bot.2026-05-11.private-key.pem /app/private-key.pem
exit
```

## 6. Deploy
```bash
flyctl deploy
```

## 7. Get your public URL
```bash
flyctl status
# Look for "Hostname" — e.g., pr-review-bot.fly.dev
```

## 8. Update GitHub App webhook URL
1. Go to GitHub App settings
2. Change webhook URL from ngrok to: `https://pr-review-bot.fly.dev/webhook`
3. Save

## 9. Scale (free tier)
```bash
flyctl scale vm shared-cpu-1x --memory=256
```

## 10. Monitor
```bash
flyctl logs
flyctl status
```

## Free tier limits
- 3 shared-cpu-1x VMs (we use 1)
- 256 MB RAM per VM
- 3 GB persistent volume total
- 160 GB outbound data/month
- Always-on (no sleep)
