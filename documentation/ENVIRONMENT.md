# YUDOR System - Environment Setup Guide

Complete guide for configuring environment variables and API keys.

---

## 🔧 Quick Setup

### 1. Copy Template
```bash
cp .env.example .env
```

### 2. Edit with Your Keys
```bash
# Open in your preferred editor
nano .env
# or
code .env
```

### 3. Add Required Keys
See sections below for how to obtain each API key.

---

## 📋 Required Environment Variables

### Anthropic Claude API (Required)
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Purpose:** Q1-Q19 analysis, YUDOR decision logic
**How to Get:**
1. Go to https://console.anthropic.com/
2. Create account or sign in
3. Navigate to API Keys section
4. Create new key
5. Copy and paste into .env

**Cost:** Pay-per-use (check current pricing)
**Rate Limits:** Check Anthropic documentation

---

### Airtable API (Required)
```bash
AIRTABLE_API_KEY=pat.your-token-here
AIRTABLE_BASE_ID=app.your-base-id-here
```

**Purpose:** Data storage, match tracking, results
**How to Get API Key:**
1. Go to https://airtable.com/create/tokens
2. Create Personal Access Token
3. Grant permissions: `data.records:read`, `data.records:write`
4. Copy token

**How to Get Base ID:**
1. Open your Airtable base
2. Go to Help → API Documentation
3. Base ID shown in URL: `https://airtable.com/appXXXXXXXX/api/docs`
4. Or check URL bar: `app` followed by alphanumeric string

**Schema Required:** See [API_REFERENCE.md](API_REFERENCE.md#airtable-schema)

---

### FootyStats API (Required)
```bash
FOOTYSTATS_API_KEY=your-footystats-key-here
```

**Purpose:** Odds data, team statistics, draw probability
**How to Get:**
1. Go to https://footystats.org/api/
2. Sign up for API access
3. Choose plan (free tier available)
4. Copy API key from dashboard

**Cost:** Free tier available, paid plans for more requests
**Rate Limits:** Depends on plan

---

## 🔒 Security Best Practices

### DO:
✅ Keep .env file in `.gitignore` (already configured)
✅ Use different keys for development/production
✅ Rotate keys regularly (every 3-6 months)
✅ Use read-only keys where possible
✅ Monitor API usage for unexpected spikes

### DON'T:
❌ Commit .env file to git
❌ Share keys in Slack/Discord/email
❌ Use production keys in development
❌ Hardcode keys in scripts
❌ Store keys in plain text documents

---

## 🧪 Testing Configuration

Verify your setup:
```bash
# Test Airtable connection
python scripts/development/test_airtable_access.py

# Test general connectivity
python scripts/development/test_fetch.py
```

---

## 🔍 Troubleshooting

### "Missing AIRTABLE_API_KEY"
**Solution:** Check .env file exists and has correct variable name

### "Invalid API key"
**Solution:**
1. Verify key copied correctly (no extra spaces)
2. Check key hasn't been revoked
3. For Airtable: ensure token has correct permissions

### ".env file not found"
**Solution:**
1. Ensure .env is in project root
2. Check you ran `cp .env.example .env`
3. Verify path: `/path/to/yudor-betting-system/.env`

### Script can't read .env
**Solution:** Scripts in subdirectories navigate up to root
- scripts/production/ → `Path(__file__).parent.parent.parent / '.env'`
- scripts/utilities/ → `Path(__file__).parent.parent.parent / '.env'`

---

## 📊 Optional Configuration

### Custom Settings
You can add additional environment variables:
```bash
# Custom model selection
CLAUDE_MODEL=claude-sonnet-4-20250514

# Custom timeout
API_TIMEOUT=30

# Debug mode
DEBUG=True
```

---

## 🔄 Key Rotation

### When to Rotate
- Every 3-6 months (scheduled)
- After team member leaves
- If key potentially exposed
- After security incident

### How to Rotate
1. Generate new key in respective service
2. Update .env file
3. Test with development scripts
4. Update production environment
5. Revoke old key after 24 hours

---

## 📁 File Structure

```
yudor-betting-system/
├── .env                    # Your actual keys (NEVER commit)
├── .env.example            # Template (safe to commit)
└── .gitignore              # Ensures .env not committed
```

---

## 🆘 Support

If you have issues:
1. Check [API_REFERENCE.md](API_REFERENCE.md) for API details
2. Verify .env.example has all required variables
3. Test with development scripts
4. Check service status pages:
   - Anthropic: https://status.anthropic.com/
   - Airtable: https://status.airtable.com/

---

**Last Updated:** 2025-11-25
**Version:** 2.0.0
