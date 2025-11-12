# PhilGEPS Scraper Service 🕷️

Python service for scraping bid opportunities from the Philippine Government Electronic Procurement System (PhilGEPS).

## Features

✅ **Persistent Browser Profile** - Maintains trust with PhilGEPS to avoid CAPTCHA challenges
✅ **Manual + Automated Login** - Manual for first 3-5 logins, then fully automated
✅ **Daily Scheduling** - Runs at 2 AM Manila time automatically
✅ **FastAPI REST API** - Endpoints for Next.js app integration
✅ **Database Integration** - Saves directly to PostgreSQL
✅ **Docker Support** - Easy deployment with Docker/Docker Compose

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd scraper-service

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required variables:**
```bash
PHILGEPS_USERNAME=jdeleon60
PHILGEPS_PASSWORD=Merritmed#01
DATABASE_URL=postgresql://user:pass@host:5432/bidscrapperv2
```

### 2. Install Dependencies

**Option A: Local Python**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

**Option B: Docker** (Recommended)
```bash
docker-compose up -d
```

---

## 🧪 Initial Setup - Build Trust with PhilGEPS

**IMPORTANT:** For the first 3-5 logins, you must do **manual login** to build trust and avoid CAPTCHA challenges.

### Step 1: Manual Login (First Time)

```bash
# Run manual login script
python -c "
from scraper.philgeps_scraper import PhilGEPSScraper
import asyncio

async def setup():
    scraper = PhilGEPSScraper()
    await scraper.login_manual()
    scraper.close()

asyncio.run(setup())
"
```

**What happens:**
1. Browser window opens
2. Credentials pre-filled
3. You solve the CAPTCHA
4. Click Login
5. Press ENTER in terminal after successful login
6. Session saved in `browser_profile/` directory

**Repeat this 3-5 times over 2-3 days to build trust.**

### Step 2: Test Automated Login

After 3-5 manual logins, test if automated login works:

```bash
python -c "
from scraper.philgeps_scraper import PhilGEPSScraper
import asyncio

async def test():
    scraper = PhilGEPSScraper()
    success = await scraper.login_automated()
    print('✅ Automated login works!' if success else '❌ Still needs manual')
    scraper.close()

asyncio.run(test())
"
```

### Step 3: Test Full Scrape

```bash
python -c "
from scraper.philgeps_scraper import PhilGEPSScraper
import asyncio

async def test_scrape():
    scraper = PhilGEPSScraper()
    result = await scraper.run_daily_scrape()
    print(f'Scraped: {result}')
    scraper.close()

asyncio.run(test_scrape())
"
```

---

## 🏃 Running the Service

### Start API + Scheduler

```bash
# Local
python main.py

# Docker
docker-compose up -d

# View logs
docker-compose logs -f scraper
```

The service will:
- ✅ Start FastAPI server on port 8000
- ✅ Schedule daily scraping at 2 AM Manila time
- ✅ Expose API endpoints for manual triggering

---

## 📡 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Get Scraping Status
```bash
GET http://localhost:8000/status
```

### Manually Trigger Scrape
```bash
POST http://localhost:8000/scrape/trigger
```

### Force Manual Login (if automated fails)
```bash
POST http://localhost:8000/login/manual
```

### Test Automated Login
```bash
POST http://localhost:8000/login/automated
```

### Get Last Scrape Results
```bash
GET http://localhost:8000/scrape/last-result
```

---

## 🔗 Integration with Next.js App

### Trigger Scraping from Next.js

```typescript
// app/api/scrape/route.ts
export async function POST() {
  const response = await fetch('http://scraper-service:8000/scrape/trigger', {
    method: 'POST'
  })

  const result = await response.json()
  return Response.json(result)
}
```

### Check Scraping Status

```typescript
// app/admin/scraper-status/page.tsx
export default async function ScraperStatusPage() {
  const res = await fetch('http://scraper-service:8000/status')
  const status = await res.json()

  return (
    <div>
      <h1>Scraper Status</h1>
      <p>In Progress: {status.scraping_in_progress ? 'Yes' : 'No'}</p>
      <p>Last Scrape: {status.last_scrape?.timestamp}</p>
      <p>Bids Scraped: {status.last_scrape?.scraped_count}</p>
    </div>
  )
}
```

---

## 📅 Scheduling

The scraper runs **daily at 2 AM Manila time** automatically.

To change the schedule, edit `scheduler.py`:

```python
# Current: Daily at 2 AM
scheduler.add_job(
    daily_scrape_job,
    CronTrigger(hour=2, minute=0, timezone='Asia/Manila')
)

# Example: Every 6 hours
scheduler.add_job(
    daily_scrape_job,
    CronTrigger(hour='*/6', timezone='Asia/Manila')
)

# Example: Twice daily (2 AM and 2 PM)
scheduler.add_job(
    daily_scrape_job,
    CronTrigger(hour='2,14', minute=0, timezone='Asia/Manila')
)
```

---

## 🗄️ Database Schema

The scraper expects this table structure:

```sql
CREATE TABLE bid_opportunities (
    id SERIAL PRIMARY KEY,
    reference_number VARCHAR(100) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    budget NUMERIC(15, 2),
    closing_date TIMESTAMP,
    procuring_entity VARCHAR(255),
    area_of_delivery VARCHAR(255),
    category VARCHAR(100),
    procurement_mode VARCHAR(100),
    scraped_at TIMESTAMP,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reference_number ON bid_opportunities(reference_number);
CREATE INDEX idx_closing_date ON bid_opportunities(closing_date);
CREATE INDEX idx_category ON bid_opportunities(category);
```

---

## 🐛 Troubleshooting

### Issue: "Automated login failed"

**Solution:** Run manual login 3-5 more times to build trust:
```bash
python -c "from scraper.philgeps_scraper import PhilGEPSScraper; import asyncio; asyncio.run(PhilGEPSScraper().login_manual())"
```

### Issue: "Browser profile not persisting"

**Solution:** Check that `browser_profile/` directory exists and has write permissions:
```bash
mkdir -p browser_profile
chmod 755 browser_profile
```

### Issue: "Database connection failed"

**Solution:** Check DATABASE_URL in .env:
```bash
# Test connection
python -c "import asyncpg, asyncio, os; asyncio.run(asyncpg.connect(os.getenv('DATABASE_URL')))"
```

### Issue: "No bids scraped"

**Possible causes:**
1. PhilGEPS changed their HTML structure → Update CSS selectors in `philgeps_scraper.py`
2. Not logged in → Check `logged_in` status
3. No opportunities posted → Check PhilGEPS website manually

**Debug:**
```python
# Run scraper with verbose output
scraper = PhilGEPSScraper()
await scraper.ensure_logged_in()
page = scraper.fetcher.get("https://philgeps.gov.ph/BulletinBoard/current_oppourtunities")
print(page.html)  # Inspect HTML to verify selectors
```

---

## 🔒 Security Notes

1. **Never commit .env file** - Contains credentials
2. **Use environment secrets** in production (Railway, Render, etc.)
3. **Rotate passwords** regularly
4. **Limit API access** - Use CORS and authentication
5. **Monitor scraping activity** - PhilGEPS may flag excessive requests

---

## 📦 Deployment

### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Add environment variables in Railway dashboard.

### Render

Create `render.yaml`:
```yaml
services:
  - type: web
    name: philgeps-scraper
    env: python
    buildCommand: pip install -r requirements.txt && playwright install chromium
    startCommand: python main.py
    envVars:
      - key: PHILGEPS_USERNAME
        sync: false
      - key: PHILGEPS_PASSWORD
        sync: false
      - key: DATABASE_URL
        sync: false
```

### Docker on VPS

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down
```

---

## 📊 Monitoring

### Check Logs

```bash
# Docker
docker-compose logs -f scraper

# Local
tail -f scraper.log
```

### Check Next Run Time

```bash
curl http://localhost:8000/status
```

### Manual Test Scrape

```bash
curl -X POST http://localhost:8000/scrape/trigger
```

---

## 🤝 Support

For issues or questions, check:
1. This README
2. PhilGEPS scraper logs
3. Database connection logs
4. Next.js app integration

---

## 📝 License

Part of the BidScrapper v2 project.
