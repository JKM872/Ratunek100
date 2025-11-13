# 🇵🇱 PHASE 3 SETUP GUIDE: Local Polish Bookmaker Scraper

## ✅ COMPLETE IMPLEMENTATION

This guide walks you through setting up the automated Polish bookmaker scraper that runs daily on your local computer (Poland IP) to bypass geo-blocking.

---

## 📋 WHAT WAS IMPLEMENTED

### 1. **Windows Automation Scripts** ✅
- `setup_local_scraper.bat` - Sets up Python venv + dependencies
- `setup_windows_task_scheduler.bat` - Configures daily auto-run at 21:00
- `run_scraper.bat` - Wrapper for Task Scheduler execution

### 2. **Enhanced Local Scraper** ✅
- `local_bookmaker_scraper.py` - Scrapes Fortuna, Superbet, STS
- Better HTML parsing with regex selectors
- File logging (`logs/scraper_YYYY-MM-DD.log`)
- Exit codes for Task Scheduler (0=success, 1=fail)
- Multiple URL fallbacks

### 3. **Backend API Endpoints** ✅
- `GET /api/bookmaker-odds?match_key=...&date=...` - Fetch odds for a match
- `GET /api/bookmaker-odds/stats` - Get scraper statistics
- Integrated in `server.js` with Supabase

### 4. **Frontend Components** ✅
- `BookmakerOdds.tsx` - Display Fortuna/Superbet/STS odds
- Integrated in `MatchCard.tsx` with border separator
- Color-coded cards (red/blue/green)
- Loading and error states

### 5. **Supabase Schema** ✅
- `bookmaker_odds` table with RLS policies
- Indexes for performance
- Automatic `updated_at` timestamp trigger

---

## 🚀 SETUP INSTRUCTIONS

### STEP 1: Supabase Database Setup

1. **Go to Supabase Dashboard**
   - https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj

2. **Create Table**
   - Open SQL Editor
   - Copy content from `supabase_bookmaker_odds_schema.sql`
   - Run the SQL script
   - Verify table created: `bookmaker_odds`

3. **Get API Keys**
   - Go to Settings → API
   - Copy `SUPABASE_URL` (already in scripts)
   - Copy `service_role` key (secret) - **needed for scraper**

---

### STEP 2: Local Computer Setup (Poland IP)

#### A. Install Python (if not installed)
```bash
# Download Python 3.11+ from python.org
# During installation, check "Add Python to PATH"
```

#### B. Run Setup Script
```bash
# Double-click: setup_local_scraper.bat
# Or run in PowerShell:
.\setup_local_scraper.bat
```

This will:
- ✅ Check Python installation
- ✅ Create virtual environment (`venv/`)
- ✅ Install dependencies (requests, beautifulsoup4, cloudscraper, supabase, etc.)
- ✅ Create `.env` file
- ✅ Create `logs/` directory

#### C. Configure Environment Variables
```bash
# Edit .env file and add your SUPABASE_KEY:

SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co
SUPABASE_KEY=eyJhbGc... # <-- YOUR service_role KEY HERE!
LOG_LEVEL=INFO
```

#### D. Test Run (Manual)
```bash
# Activate venv
.\venv\Scripts\activate.bat

# Run scraper
python local_bookmaker_scraper.py

# Check logs
type logs\scraper_2025-01-15.log
```

**Expected Output:**
```
🇵🇱 POLISH BOOKMAKER SCRAPER - STARTING
🔍 Starting Fortuna scraping...
✅ Fortuna: Scraped 45 matches
🔍 Starting Superbet scraping...
✅ Superbet: Scraped 38 matches
🔍 Starting STS scraping...
✅ STS: Scraped 42 matches
📤 Uploading 125 matches to Supabase...
✅ Upload complete: 125 success, 0 errors
✅ SUCCESS: Scraper completed
```

---

### STEP 3: Windows Task Scheduler Setup

#### A. Run Scheduler Setup (AS ADMINISTRATOR!)
```bash
# Right-click setup_windows_task_scheduler.bat
# Select "Run as administrator"
```

This will:
- ✅ Create scheduled task "PolishBookmakerScraper"
- ✅ Set daily schedule at 21:00 (9:00 PM)
- ✅ Configure to run even if user not logged in

#### B. Verify Task Created
```bash
# PowerShell:
schtasks /query /tn "PolishBookmakerScraper"
```

#### C. Manual Test Run
```bash
# PowerShell (as admin):
schtasks /run /tn "PolishBookmakerScraper"

# Check output:
type logs\task_scheduler.log
```

---

### STEP 4: Backend Setup

#### A. Add Supabase Key to .env (if not already)
```bash
# Edit .env in project root:

SUPABASE_URL=https://bfslhqnxsgmdyptrqshj.supabase.co
SUPABASE_KEY=eyJhbGc... # <-- YOUR service_role KEY
```

#### B. Restart Backend
```bash
# PowerShell:
node server.js
```

**Expected Output:**
```
✅ Using Supabase database
🚀 Server running on port 5000
```

#### C. Test API Endpoints
```bash
# Get bookmaker odds
curl http://localhost:5000/api/bookmaker-odds?match_key=legia_warszawa_vs_rakow_czestochowa_2025-01-15

# Get statistics
curl http://localhost:5000/api/bookmaker-odds/stats
```

---

### STEP 5: Frontend Setup

#### A. Install Dependencies (First Time Only)
```bash
cd frontend
npm install
```

#### B. Start Development Server
```bash
npm run dev
```

**Expected Output:**
```
VITE v5.0.0  ready in 350 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

#### C. Test Frontend
1. Open http://localhost:3000
2. View Dashboard → See stats
3. View Matches → Click on match card
4. **Scroll down** → See "Kursy Polskich Bukmacherów 🇵🇱" section
5. Verify odds from Fortuna/Superbet/STS displayed

---

### STEP 6: Production Build

#### A. Build Frontend for Production
```bash
cd frontend
npm run build
```

This outputs to `../public/` (served by Express)

#### B. Deploy Backend
```bash
# Backend serves both API and frontend
node server.js
```

#### C. Access Production
- Open http://localhost:5000
- Backend serves static files from `public/`
- API routes work at `/api/*`

---

## 📊 EXPECTED RESULTS

### Scraper Output
- ✅ 50-100+ matches scraped daily from Polish bookmakers
- ✅ Fortuna (PRIORITY), Superbet, STS coverage
- ✅ 80%+ matches have all 3 bookmakers
- ✅ Data stored in Supabase (globally accessible)
- ✅ Logs in `logs/` directory

### Backend API
- ✅ `/api/bookmaker-odds` returns odds by match_key
- ✅ `/api/bookmaker-odds/stats` returns coverage statistics
- ✅ Fast queries with Supabase indexes

### Frontend UI
- ✅ BookmakerOdds component displays in MatchCard
- ✅ Color-coded cards: Fortuna (red), Superbet (blue), STS (green)
- ✅ "PRIORITY" badge for Fortuna
- ✅ Loading/error states handled gracefully
- ✅ Shows "Brak kursów" if no data

### Email Notifications
- ✅ Email includes Polish bookmaker odds (not "Brak kursów")
- ✅ Formatted with bookmaker names

---

## 🔍 TROUBLESHOOTING

### Issue: "No matches scraped"
**Solution:**
- Check internet connection (Poland IP required!)
- Verify bookmaker websites not changed selectors
- Check logs: `type logs\scraper_*.log`
- Try different FORTUNA_URLS in script

### Issue: "Supabase connection error"
**Solution:**
- Verify `.env` has correct `SUPABASE_KEY` (service_role)
- Check Supabase dashboard → Settings → API
- Test connection: `python -c "from supabase import create_client; ..."`

### Issue: "Task Scheduler not running"
**Solution:**
- Open Task Scheduler app (taskschd.msc)
- Find "PolishBookmakerScraper" task
- Check "Last Run Result" (should be 0x0 for success)
- Check logs: `type logs\task_scheduler.log`
- Manually run: `schtasks /run /tn "PolishBookmakerScraper"`

### Issue: "Frontend shows 'Brak kursów'"
**Solution:**
- Verify scraper ran successfully (check logs)
- Verify Supabase has data (check SQL editor)
- Verify backend `/api/bookmaker-odds` returns data (curl test)
- Check browser console for errors (F12)
- Verify match_key generation matches scraper format

---

## 📁 FILE STRUCTURE

```
Ratowanie/
├── setup_local_scraper.bat              # Python venv setup
├── setup_windows_task_scheduler.bat     # Task Scheduler config
├── run_scraper.bat                      # Task Scheduler wrapper
├── local_bookmaker_scraper.py           # Main scraper script
├── supabase_bookmaker_odds_schema.sql   # Database schema
├── .env                                 # Environment variables
├── logs/                                # Scraper logs
│   ├── scraper_2025-01-15.log
│   └── task_scheduler.log
├── server.js                            # Backend with new endpoints
└── frontend/
    └── src/
        ├── components/
        │   ├── BookmakerOdds.tsx        # Bookmaker odds display
        │   └── MatchCard.tsx            # Updated with BookmakerOdds
        └── lib/
            └── utils.ts                 # Added generateMatchKey()
```

---

## 🎯 SUCCESS CHECKLIST

- [ ] Supabase table `bookmaker_odds` created
- [ ] Python venv setup completed (`setup_local_scraper.bat`)
- [ ] `.env` file configured with `SUPABASE_KEY`
- [ ] Manual scraper test successful (50+ matches)
- [ ] Task Scheduler configured (runs daily at 21:00)
- [ ] Backend API endpoints working (`/api/bookmaker-odds`)
- [ ] Frontend displays bookmaker odds in MatchCard
- [ ] End-to-end flow tested (scraper → Supabase → API → UI)

---

## 🚦 NEXT STEPS (PHASE 4 & 5)

### PHASE 4: Supabase Authentication
- User registration/login
- Protected routes
- User preferences (favorite sports, teams)
- Email subscription management

### PHASE 5: Stripe Payment Integration
- Subscription plans (Free, Premium, Pro)
- Payment flow
- Access control based on subscription
- Billing dashboard

---

## 📞 SUPPORT

If you encounter issues:
1. Check logs: `logs/scraper_*.log` and `logs/task_scheduler.log`
2. Verify Supabase connection and table exists
3. Test API endpoints with curl
4. Check browser console for frontend errors

**Status:** ✅ PHASE 3 COMPLETE - Ready for testing!
