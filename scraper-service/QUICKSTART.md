# 🚀 Quick Start Guide

Get the PhilGEPS scraper running in **5 minutes**.

---

## Step 1: Setup (2 minutes)

```bash
cd scraper-service

# Run setup script
./setup.sh

# Edit credentials
nano .env
```

**Required in .env:**
```bash
PHILGEPS_USERNAME=jdeleon60
PHILGEPS_PASSWORD=Merritmed#01
DATABASE_URL=postgresql://user:pass@host:5432/bidscrapperv2
```

---

## Step 2: First-Time Login (2 minutes)

**IMPORTANT:** Do this 3-5 times over 2-3 days to build trust.

```bash
# Activate environment
source venv/bin/activate

# Run test suite
python test_scraper.py

# Select option 1: "First time setup (manual login only)"
```

**What happens:**
1. Browser opens with credentials filled
2. You solve CAPTCHA
3. Click Login
4. Press ENTER in terminal
5. Session saved ✅

**Repeat 3-5 times** (once per day for 3-5 days).

---

## Step 3: Test Automated Login (30 seconds)

After 3-5 manual logins, test if automation works:

```bash
python test_scraper.py

# Select option 2: "Test automated login"
```

✅ **Works?** → You're ready for daily scraping!
❌ **Fails?** → Do 2-3 more manual logins.

---

## Step 4: Run Daily Scraper (Forever)

```bash
# Start the service (API + Scheduler)
python main.py
```

The scraper will:
- ✅ Run at 2 AM Manila time daily
- ✅ Expose API on http://localhost:8000
- ✅ Save bids to your database automatically

---

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Setup
cp .env.example .env
nano .env  # Add credentials

# Build and run
docker-compose up -d

# First login (inside container)
docker-compose exec scraper python test_scraper.py

# View logs
docker-compose logs -f scraper
```

---

## 🧪 Testing

### Test Full Pipeline

```bash
python test_scraper.py

# Select option 4: "Full pipeline test"
```

This will:
1. Login to PhilGEPS
2. Scrape bid opportunities
3. Save to database
4. Show results

---

## 📊 Monitoring

### Check if scraper is running

```bash
curl http://localhost:8000/health
```

### Check last scrape results

```bash
curl http://localhost:8000/status
```

### Manually trigger scrape

```bash
curl -X POST http://localhost:8000/scrape/trigger
```

---

## ⚠️ Troubleshooting

### "Automated login failed"
**Fix:** Run more manual logins (option 1)

### "No bids scraped"
**Possible causes:**
- No opportunities posted on PhilGEPS today
- HTML selectors need updating
- Not logged in

**Debug:**
```bash
# Check if you can login manually
python test_scraper.py  # Option 1
```

### "Database connection failed"
**Fix:** Check DATABASE_URL in .env

```bash
# Test connection
python -c "import asyncpg, asyncio, os; from dotenv import load_dotenv; load_dotenv(); asyncio.run(asyncpg.connect(os.getenv('DATABASE_URL')))"
```

---

## 🎯 Next Steps

1. ✅ Complete 3-5 manual logins
2. ✅ Verify automated login works
3. ✅ Run full pipeline test
4. ✅ Deploy to production (Railway, Render, or VPS)
5. ✅ Integrate with Next.js frontend

---

## 📚 More Info

- **Full docs:** See [README.md](./README.md)
- **API endpoints:** http://localhost:8000/docs (when running)
- **Scraper code:** `scraper/philgeps_scraper.py`
- **Schedule:** `scheduler.py` (change from 2 AM if needed)

---

**Questions?** Check the [README.md](./README.md) for detailed troubleshooting.
