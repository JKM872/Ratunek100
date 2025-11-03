const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Database connection
// Check if we're on Heroku (GitHub Actions scraper writes to /app/data/matches.db)
let DB_PATH;
if (process.env.DATABASE_PATH) {
  DB_PATH = process.env.DATABASE_PATH;
} else if (fs.existsSync('/app/data/matches.db')) {
  DB_PATH = '/app/data/matches.db';  // Heroku
} else {
  DB_PATH = path.join(__dirname, 'outputs', 'matches.db');  // Local
}

console.log('📂 Database path:', DB_PATH);

let db;
try {
  // Use OPEN_READONLY if database exists, otherwise OPEN_READWRITE to allow creation
  const openMode = fs.existsSync(DB_PATH) ? sqlite3.OPEN_READONLY : sqlite3.OPEN_READWRITE;
  db = new sqlite3.Database(DB_PATH, openMode, (err) => {
    if (err) {
      console.error('❌ Database connection error:', err.message);
      console.log('💡 Run Python scraper first to create the database');
    } else {
      console.log('✅ Connected to SQLite database');
    }
  });
} catch (err) {
  console.error('❌ Database error:', err);
}

// ==================== API ENDPOINTS ====================

// GET /api/health - Health check
app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    message: 'API is running',
    timestamp: new Date().toISOString(),
    database: db ? 'connected' : 'disconnected'
  });
});

// GET /api/matches - Pobierz mecze
app.get('/api/matches', (req, res) => {
  if (!db) {
    return res.status(503).json({
      success: false,
      error: 'Database not available. Run Python scraper first.'
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
  path.join(__dirname, 'public')                              // Fallback: public
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
  console.log('⚠️  React build not found in any location');
  app.get('*', (req, res) => {
    if (req.path.startsWith('/api/')) {
      return res.status(404).json({ success: false, error: 'API endpoint not found' });
    }
    res.status(404).json({
      success: false,
      error: 'React build not found. Please run: cd example_ui_app/client && npm run build'
    });
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
