# Railway Deployment Guide

## 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

## 2. Login
```bash
railway login
```
- Opens browser → authorize with GitHub

## 3. Initialize project
```bash
railway init
```
- Select **Create new project**
- Name: `pr-review-bot`
- Select **Empty project**

## 4. Add environment variables
```bash
railway variables set GROQ_API_KEY="your_groq_key"
railway variables set GITHUB_WEBHOOK_SECRET="your_webhook_secret"
railway variables set GITHUB_APP_ID="3677095"
railway variables set SUPABASE_URL="https://gcfhrudsiuzocvnqgccc.supabase.co"
railway variables set SUPABASE_KEY="your_supabase_key"
```

## 5. Upload private key
```bash
# Create a base64 encoded version of your .pem file
base64 -i pullrequest-review-bot.2026-05-11.private-key.pem > private-key.txt

# Set as variable
railway variables set GITHUB_PRIVATE_KEY="$(cat private-key.txt)"
```

## 6. Update config.py to read from base64
Add this to `config.py`:
```python
import base64

# In Config class, add:
GITHUB_PRIVATE_KEY: str = os.getenv("GITHUB_PRIVATE_KEY", "")
if GITHUB_PRIVATE_KEY:
    # Write to file for PyGitHub
    with open("/tmp/private-key.pem", "wb") as f:
        f.write(base64.b64decode(GITHUB_PRIVATE_KEY))
    GITHUB_PRIVATE_KEY_PATH = "/tmp/private-key.pem"
```

## 7. Deploy
```bash
railway up
```

## 8. Get your public URL
```bash
railway status
```
- Copy the URL (e.g., `https://pr-review-bot.up.railway.app`)

## 9. Update GitHub App webhook URL
1. Go to GitHub App settings
2. Change webhook URL to: `https://pr-review-bot.up.railway.app/webhook`
3. Save

## Railway Free Tier
- 500 hours/month (always-on for ~20 days)
- $5 credit monthly
- No credit card required
- Automatic HTTPS
- GitHub integration

## If Railway asks for payment
- Use the $5 monthly credit
- It's free unless you exceed limits
