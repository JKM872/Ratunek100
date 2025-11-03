# Quick Start Guide

## Dashboard is LIVE ✅

**URL**: https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/

## Status

- ✅ **React UI**: Deployed and loading
- ✅ **API Backend**: Running on port 3001
- ⏳ **Database**: Empty (needs scraper data)

## What to Do Now

### 1️⃣ Populate Database (Pick ONE)

#### A) GitHub Actions (Automatic - Recommended)
```
Go to: https://github.com/YourUsername/Ratowanie/actions
Select: "Midnight Auto Scraping (All Sports)"  
Click: "Run workflow"
Wait: ~30 min for completion
```

#### B) Run Scraper Locally
```powershell
cd c:\Users\jakub\Downloads\Ratowanie
python livesport_odds_api_client.py --parallel
```

#### C) Run Specific Sport Locally  
```powershell
python scrape_and_notify.py --sports football --date 2025-11-04
```

### 2️⃣ Verify Data Appears

Once scraper completes:
- Refresh: https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/
- Dashboard should show:
  - **Total Matches**: ~500-2500 depending on date/sports
  - **Live Odds**: Bookmaker names and odds
  - **Form Analysis**: Teams with form advantage

### 3️⃣ Test API Manually

```bash
# Windows PowerShell
$health = Invoke-WebRequest https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/api/health | ConvertFrom-Json
$health | Format-Table

# Get matches (after database has data)
$matches = Invoke-WebRequest "https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/api/matches?limit=5" | ConvertFrom-Json
$matches.data | Select-Object match_date, home_team, away_team, sport | Format-Table
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Database not available" | Run scraper first |
| Blank dashboard page | Check browser console (F12) for JS errors |
| API timeout (30+ sec) | Database hasn't loaded yet |
| 404 on /api/matches | Backend running but database missing |

## Commands Reference

```bash
# Check app status
heroku logs -a livesport-scraper-ui --tail

# Trigger GitHub Actions manually
# Go to: https://github.com/YourUsername/Ratowanie/actions

# Run all sports scraper locally
python livesport_odds_api_client.py --parallel

# Run single sport
python scrape_and_notify.py --sports football --date 2025-11-04

# Deploy new changes
git push heroku main

# View Heroku app
open https://livesport-scraper-ui-0393f6f2096e.herokuapp.com/
```

## Database Location

- **Local development**: `outputs/matches.db`
- **Heroku production**: `/app/data/matches.db` (GitHub Actions) or `/app/outputs/matches.db` (fallback)

## File Structure

```
Ratowanie/
├── server.js                          # Express backend (Heroku entry point)
├── example_ui_app/client/
│   ├── src/                           # React source code
│   ├── dist/                          # Built React app (committed for Heroku)
│   └── package.json                   # React dependencies
├── livesport_odds_api_client.py       # Python scraper
├── .github/workflows/                 # GitHub Actions jobs
└── outputs/                           # Local database location
    └── matches.db
```

## Performance Tips

- 🚀 Use `--parallel` flag for 10x faster scraping
- ⏱️ First run: ~30 min for 2500+ matches
- 📊 Subsequent runs: ~5 min (updates only)
- 🔄 Automatic daily runs: Set GitHub Actions schedule

## Need Help?

1. **Dashboard not loading?** → Check browser console (F12)
2. **API times out?** → Run scraper first
3. **GitHub Actions failed?** → Check Actions tab for logs
4. **Need to redeploy?** → `git push heroku main`

---

🎉 **Deployment Complete!** Enjoy your sports data dashboard.
