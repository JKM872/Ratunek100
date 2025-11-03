const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.SCRAPER_API_KEY || 'super-secret-key-12345';

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));  // Larger limit for webhook data

// API Key verification middleware
const verifyApiKey = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ 
      success: false, 
      error: 'Missing or invalid Authorization header' 
    });
  }
  
  const token = authHeader.substring(7);
  if (token !== API_KEY) {
    return res.status(403).json({ 
      success: false, 
      error: 'Invalid API key' 
    });
  }
  
  next();
};

// Database connection
// Check if we're on Heroku (GitHub Actions scraper writes to /app/data/matches.db)
let DB_PATH;
if (process.env.DATABASE_PATH) {
  DB_PATH = process.env.DATABASE_PATH;
} else if (fs.existsSync('/app/data/matches.db')) {
  DB_PATH = '/app/data/matches.db';  // Heroku - GitHub Actions scraper writes here
} else if (fs.existsSync(path.join(__dirname, 'outputs', 'matches.db'))) {
  DB_PATH = path.join(__dirname, 'outputs', 'matches.db');  // Local existing
} else {
  DB_PATH = path.join(__dirname, 'outputs', 'matches.db');  // Local - will create on scraper run
}

// Ensure data directory exists
const dbDir = path.dirname(DB_PATH);
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
  console.log('� Created directory:', dbDir);
}

console.log('�📂 Database path:', DB_PATH);
console.log('📂 Database exists:', fs.existsSync(DB_PATH) ? 'YES' : 'NO');

let db = null;
let dbConnected = false;

try {
  // Use READWRITE to allow webhook writes, create if doesn't exist
  const openMode = fs.existsSync(DB_PATH) 
    ? sqlite3.OPEN_READWRITE 
    : sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE;
    
  db = new sqlite3.Database(DB_PATH, openMode, (err) => {
    if (err) {
      console.error('❌ Database connection error:', err.message);
      dbConnected = false;
    } else {
      console.log('✅ Connected to SQLite database');
      dbConnected = true;
      
      // Create table if doesn't exist
      db.run(`
        CREATE TABLE IF NOT EXISTS matches (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          sport TEXT,
          match_date TEXT,
          match_time TEXT,
          home_team TEXT,
          away_team TEXT,
          home_odds REAL,
          away_odds REAL,
          draw_odds REAL,
          home_win_percentage REAL,
          draw_percentage REAL,
          away_win_percentage REAL,
          avg_home_goals REAL,
          avg_away_goals REAL,
          qualifies INTEGER,
          created_at TEXT,
          all_odds TEXT,
          bookmaker_name TEXT,
          bookmaker_url TEXT
        )
      `, (err) => {
        if (err) {
          console.error('❌ Table creation error:', err.message);
        } else {
          console.log('✅ Database schema ready');
        }
      });
    }
  });
} catch (err) {
  console.error('❌ Database error:', err);
  dbConnected = false;
}

// ==================== API ENDPOINTS ====================

// GET /api/health - Health check
app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    message: 'API is running',
    timestamp: new Date().toISOString(),
    database: dbConnected ? 'connected' : 'disconnected',
    databasePath: DB_PATH,
    databaseExists: fs.existsSync(DB_PATH)
  });
});

// POST /api/webhook/matches - Receive matches from scraper
app.post('/api/webhook/matches', verifyApiKey, async (req, res) => {
  try {
    const { matches, date, sport } = req.body;
    
    console.log('\n' + '='.repeat(70));
    console.log('📥 WEBHOOK: Received data from scraper');
    console.log('='.repeat(70));
    console.log(`📅 Date: ${date}`);
    console.log(`⚽ Sport: ${sport}`);
    console.log(`📊 Matches: ${matches ? matches.length : 0}`);
    
    if (!matches || !Array.isArray(matches)) {
      return res.status(400).json({ 
        success: false, 
        error: 'Invalid data format - matches must be an array' 
      });
    }
    
    if (!db || !dbConnected) {
      return res.status(503).json({ 
        success: false, 
        error: 'Database not available' 
      });
    }
    
    let saved = 0;
    let errors = 0;
    
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO matches (
        sport, match_date, match_time, home_team, away_team,
        home_odds, away_odds, draw_odds,
        home_win_percentage, draw_percentage, away_win_percentage,
        avg_home_goals, avg_away_goals,
        qualifies, created_at, all_odds, bookmaker_name, bookmaker_url
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    for (const match of matches) {
      try {
        const all_odds_json = match.all_odds
          ? (typeof match.all_odds === 'string' ? match.all_odds : JSON.stringify(match.all_odds))
          : null;
        
        stmt.run(
          match.sport || sport,
          match.match_date || date,
          match.match_time || null,
          match.home_team,
          match.away_team,
          match.home_odds || null,
          match.away_odds || null,
          match.draw_odds || null,
          match.home_win_percentage || null,
          match.draw_percentage || null,
          match.away_win_percentage || null,
          match.avg_home_goals || null,
          match.avg_away_goals || null,
          match.qualifies || 0,
          match.created_at || new Date().toISOString(),
          all_odds_json,
          match.bookmaker_name || null,
          match.bookmaker_url || null
        );
        saved++;
      } catch (err) {
        console.error(`❌ Error saving match ${match.home_team} vs ${match.away_team}:`, err.message);
        errors++;
      }
    }
    
    stmt.finalize();
    
    console.log(`✅ Saved ${saved} matches to database`);
    if (errors > 0) {
      console.log(`⚠️  ${errors} matches failed to save`);
    }
    
    res.json({ 
      success: true,
      message: 'Matches saved successfully',
      saved,
      errors,
      total: matches.length
    });
  } catch (err) {
    console.error('❌ Webhook error:', err);
    res.status(500).json({ 
      success: false, 
      error: err.message 
    });
  }
});

// GET /api/matches - Pobierz mecze
app.get('/api/matches', (req, res) => {
  if (!db || !dbConnected) {
    return res.status(503).json({
      success: false,
      error: 'Database not available',
      message: 'Run Python scraper first to create the database',
      database: {
        path: DB_PATH,
        exists: fs.existsSync(DB_PATH),
        connected: dbConnected
      }
    });
  }

  const { date, sport, qualifies, limit = 100 } = req.query;
  
  let query = 'SELECT * FROM matches WHERE 1=1';
  const params = [];
  
  if (date) {
    query += ' AND match_date = ?';
    params.push(date);
  }
  
  if (sport) {
    query += ' AND sport = ?';
    params.push(sport);
  }
  
  if (qualifies === 'true' || qualifies === '1') {
    query += ' AND qualifies = 1';
  }
  
  query += ' ORDER BY match_date DESC, match_time ASC, home_team ASC LIMIT ?';
  params.push(parseInt(limit));
  
  db.all(query, params, (err, rows) => {
    if (err) {
      console.error('❌ Query error:', err);
      return res.status(500).json({ success: false, error: err.message });
    }
    
    // Parsuj JSON fields
    const matches = rows.map(row => {
      const match = { ...row };
      
      // Parse JSON strings
      if (match.all_odds) {
        try {
          match.all_odds = JSON.parse(match.all_odds);
        } catch (e) {
          match.all_odds = {};
        }
      }
      
      if (match.h2h_last5) {
        try {
          match.h2h_last5 = JSON.parse(match.h2h_last5);
        } catch (e) {
          match.h2h_last5 = [];
        }
      }
      
      if (match.bookmakers_found) {
        match.bookmakers_found = match.bookmakers_found.split(', ').filter(Boolean);
      }
      
      // Parse forms (string to array)
      ['home_form', 'away_form', 'home_form_overall', 'away_form_overall'].forEach(field => {
        if (match[field]) {
          match[field] = match[field].split('-').filter(Boolean);
        }
      });
      
      // Convert boolean-like integers
      match.qualifies = Boolean(match.qualifies);
      match.form_advantage = Boolean(match.form_advantage);
      
      return match;
    });
    
    res.json({
      success: true,
      count: matches.length,
      matches
    });
  });
});

// GET /api/stats - Statystyki
app.get('/api/stats', (req, res) => {
  if (!db) {
    return res.status(503).json({
      success: false,
      error: 'Database not available'
    });
  }

  const queries = {
    total: 'SELECT COUNT(*) as value FROM matches',
    qualifying: 'SELECT COUNT(*) as value FROM matches WHERE qualifies = 1',
    sports: 'SELECT COUNT(DISTINCT sport) as value FROM matches',
    dates: 'SELECT COUNT(DISTINCT match_date) as value FROM matches',
    lastUpdate: 'SELECT MAX(scraped_at) as value FROM matches'
  };
  
  const results = {};
  const promises = Object.entries(queries).map(([key, query]) => {
    return new Promise((resolve, reject) => {
      db.get(query, (err, row) => {
        if (err) reject(err);
        else {
          results[key] = row ? row.value : 0;
          resolve();
        }
      });
    });
  });
  
  Promise.all(promises)
    .then(() => {
      res.json({
        success: true,
        stats: {
          total_matches: results.total,
          qualifying_matches: results.qualifying,
          unique_sports: results.sports,
          date_range: results.dates,
          last_update: results.lastUpdate
        }
      });
    })
    .catch(err => {
      res.status(500).json({ success: false, error: err.message });
    });
});

// GET /api/sports - Lista sportów
app.get('/api/sports', (req, res) => {
  if (!db) {
    return res.status(503).json({
      success: false,
      error: 'Database not available'
    });
  }

  db.all(
    `SELECT 
      sport, 
      COUNT(*) as total_count,
      SUM(CASE WHEN qualifies = 1 THEN 1 ELSE 0 END) as qualifying_count
    FROM matches 
    GROUP BY sport 
    ORDER BY total_count DESC`,
    (err, rows) => {
      if (err) {
        return res.status(500).json({ success: false, error: err.message });
      }
      res.json({ success: true, sports: rows });
    }
  );
});

// GET /api/dates - Lista dat
app.get('/api/dates', (req, res) => {
  if (!db) {
    return res.status(503).json({
      success: false,
      error: 'Database not available'
    });
  }

  db.all(
    `SELECT 
      match_date, 
      COUNT(*) as total_count,
      SUM(CASE WHEN qualifies = 1 THEN 1 ELSE 0 END) as qualifying_count
    FROM matches 
    GROUP BY match_date 
    ORDER BY match_date DESC 
    LIMIT 30`,
    (err, rows) => {
      if (err) {
        return res.status(500).json({ success: false, error: err.message });
      }
      res.json({ success: true, dates: rows });
    }
  );
});

// GET /api/bookmakers - Lista bukmacherów
app.get('/api/bookmakers', (req, res) => {
  if (!db) {
    return res.status(503).json({
      success: false,
      error: 'Database not available'
    });
  }

  db.all(
    `SELECT DISTINCT bookmakers_found 
    FROM matches 
    WHERE bookmakers_found IS NOT NULL AND bookmakers_found != ''`,
    (err, rows) => {
      if (err) {
        return res.status(500).json({ success: false, error: err.message });
      }
      
      // Flatten and deduplicate
      const bookmakers = new Set();
      rows.forEach(row => {
        if (row.bookmakers_found) {
          row.bookmakers_found.split(', ').forEach(bm => bookmakers.add(bm.trim()));
        }
      });
      
      res.json({
        success: true,
        bookmakers: Array.from(bookmakers).sort()
      });
    }
  );
});

// Catch-all route - serve index.html for SPA routing
// Try multiple locations for React build
const buildPaths = [
  path.join(__dirname, 'example_ui_app', 'client', 'dist'),  // Primary: example_ui_app
  path.join(__dirname, 'client', 'dist'),                     // Secondary: root client
];

let buildDir = null;
for (const buildPath of buildPaths) {
  if (fs.existsSync(buildPath)) {
    buildDir = buildPath;
    console.log('✅ Found React build at:', buildDir);
    break;
  }
}

if (buildDir) {
  // Serve static files
  app.use(express.static(buildDir));
  
  // Catch-all for SPA routing
  app.get('*', (req, res) => {
    // Don't intercept API calls that don't exist
    if (req.path.startsWith('/api/')) {
      return res.status(404).json({ success: false, error: 'API endpoint not found' });
    }
    res.sendFile(path.join(buildDir, 'index.html'));
  });
} else {
  console.log('⚠️  React build not found - using fallback diagnostic UI');
  
  // Serve fallback diagnostic UI
  const publicPath = path.join(__dirname, 'public');
  if (fs.existsSync(publicPath)) {
    app.use(express.static(publicPath));
    console.log('✅ Serving fallback UI from:', publicPath);
  }
  
  app.get('*', (req, res) => {
    if (req.path.startsWith('/api/')) {
      return res.status(404).json({ success: false, error: 'API endpoint not found' });
    }
    
    // Try to serve public/index.html
    const fallbackPath = path.join(__dirname, 'public', 'index.html');
    if (fs.existsSync(fallbackPath)) {
      return res.sendFile(fallbackPath);
    }
    
    // Last resort - serve inline diagnostic UI
    return res.status(200).send(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Livesport Scraper - Diagnostic UI</title>
        <style>
          body { font-family: Arial; padding: 20px; background: #f5f5f5; }
          .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
          h1 { color: #333; }
          .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
          .warning { background: #fff3cd; border: 1px solid #ffc107; color: #856404; }
          .success { background: #d4edda; border: 1px solid #28a745; color: #155724; }
          button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
          button:hover { background: #0056b3; }
          #result { margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 4px; white-space: pre-wrap; font-family: monospace; max-height: 400px; overflow-y: auto; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>🏏 Livesport Scraper Dashboard</h1>
          <p>React build not found. Using diagnostic fallback UI.</p>
          
          <div class="status warning">
            ⚠️ React build not found at: /app/example_ui_app/client/dist/
          </div>
          
          <h2>Test API Endpoints:</h2>
          <button onclick="testHealth()">Test /api/health</button>
          <button onclick="testMatches()">Test /api/matches</button>
          <button onclick="testStats()">Test /api/stats</button>
          
          <div id="result"></div>
          
          <h2>Setup Instructions:</h2>
          <ol>
            <li>Run Python scraper to create database: <code>python livesport_odds_api_client.py --parallel</code></li>
            <li>Build React UI: <code>cd example_ui_app/client && npm run build</code></li>
            <li>Redeploy to Heroku: <code>git push heroku main</code></li>
          </ol>
        </div>
        
        <script>
          async function testHealth() {
            const result = document.getElementById('result');
            result.textContent = 'Testing...';
            try {
              const response = await fetch('/api/health');
              const data = await response.json();
              result.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
              result.textContent = 'Error: ' + e.message;
            }
          }
          
          async function testMatches() {
            const result = document.getElementById('result');
            result.textContent = 'Testing...';
            try {
              const response = await fetch('/api/matches?limit=5');
              const data = await response.json();
              result.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
              result.textContent = 'Error: ' + e.message;
            }
          }
          
          async function testStats() {
            const result = document.getElementById('result');
            result.textContent = 'Testing...';
            try {
              const response = await fetch('/api/stats');
              const data = await response.json();
              result.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
              result.textContent = 'Error: ' + e.message;
            }
          }
        </script>
      </body>
      </html>
    `);
  });
}

// Error handling
app.use((err, req, res, next) => {
  console.error('❌ Server error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 API available at http://localhost:${PORT}/api`);
  console.log(`🌐 Frontend available at http://localhost:${PORT}\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down gracefully...');
  if (db) {
    db.close((err) => {
      if (err) {
        console.error('❌ Error closing database:', err.message);
      }
      console.log('✅ Database connection closed');
      process.exit(0);
    });
  } else {
    process.exit(0);
  }
});
