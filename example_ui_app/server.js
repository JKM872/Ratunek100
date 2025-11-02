/**
 * 🎯 PRZYKŁADOWA APLIKACJA UI - Odbieranie danych ze scrapera
 * ===========================================================
 * 
 * Ta aplikacja odbiera dane z GitHub Actions scrapera i zapisuje do bazy.
 * 
 * Deployment: Railway / Render / Vercel / localhost + ngrok
 * 
 * INSTALACJA:
 *   npm install express cors sqlite3
 * 
 * URUCHOMIENIE:
 *   node server.js
 * 
 * KONFIGURACJA:
 *   export SCRAPER_API_KEY="super-secret-key-12345"
 *   export PORT=3000
 */

const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.SCRAPER_API_KEY || 'super-secret-key-12345';

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' })); // Duży limit dla wielu meczów

// Database setup
const DB_DIR = path.join(__dirname, 'data');
if (!fs.existsSync(DB_DIR)) {
  fs.mkdirSync(DB_DIR, { recursive: true });
}

const DB_PATH = path.join(DB_DIR, 'matches.db');
let db = new sqlite3.Database(DB_PATH);

// Inicjalizacja bazy danych
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS matches (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      
      -- Podstawowe info
      match_date TEXT NOT NULL,
      match_time TEXT,
      sport TEXT NOT NULL,
      league TEXT,
      
      -- Zespoły
      home_team TEXT NOT NULL,
      away_team TEXT NOT NULL,
      
      -- Kursy
      home_odds REAL,
      draw_odds REAL,
      away_odds REAL,
      best_home_bookmaker TEXT,
      best_away_bookmaker TEXT,
      bookmakers_found TEXT, -- JSON array
      all_odds TEXT, -- JSON object
      
      -- H2H Stats
      h2h_count INTEGER DEFAULT 0,
      home_wins_in_h2h_last5 INTEGER DEFAULT 0,
      draws_last_5 INTEGER DEFAULT 0,
      away_wins_in_h2h INTEGER DEFAULT 0,
      win_rate REAL,
      h2h_last5 TEXT, -- JSON array
      
      -- Forma
      home_form_overall TEXT, -- JSON array [W,W,L,D,W]
      away_form_overall TEXT, -- JSON array
      form_advantage BOOLEAN DEFAULT 0,
      
      -- Qualifikacja
      qualifies BOOLEAN DEFAULT 0,
      
      -- URLs
      match_url TEXT,
      h2h_url TEXT,
      
      -- Metadata
      scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      source TEXT DEFAULT 'github_actions',
      
      -- Indeksy dla szybkiego wyszukiwania
      UNIQUE(match_date, home_team, away_team, sport)
    )
  `);
  
  // Indeksy
  db.run(`CREATE INDEX IF NOT EXISTS idx_match_date ON matches(match_date)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_sport ON matches(sport)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_qualifies ON matches(qualifies)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_scraped_at ON matches(scraped_at)`);
  
  console.log('✅ Baza danych zainicjalizowana');
});

// ============================================================================
// MIDDLEWARE - Weryfikacja API Key
// ============================================================================
function verifyApiKey(req, res, next) {
  const authHeader = req.headers.authorization;
  
  // Jeśli API_KEY nie jest ustawiony, pomiń weryfikację (development)
  if (!process.env.SCRAPER_API_KEY) {
    console.warn('⚠️  SCRAPER_API_KEY nie ustawiony - autoryzacja wyłączona!');
    return next();
  }
  
  if (!authHeader || authHeader !== `Bearer ${API_KEY}`) {
    console.error('❌ Nieautoryzowany dostęp:', authHeader);
    return res.status(401).json({ 
      success: false, 
      error: 'Unauthorized - Invalid API Key' 
    });
  }
  
  next();
}

// ============================================================================
// ENDPOINT 1: Health Check
// ============================================================================
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'Aplikacja UI działa!',
    timestamp: new Date().toISOString(),
    database: DB_PATH
  });
});

// ============================================================================
// ENDPOINT 2: Webhook - Odbierz mecze ze scrapera (GŁÓWNY ENDPOINT)
// ============================================================================
app.post('/api/webhook/matches', verifyApiKey, async (req, res) => {
  try {
    const { date, sport, matches, qualified_count, total_count, timestamp } = req.body;
    
    console.log('\n' + '='.repeat(70));
    console.log('📥 OTRZYMANO DANE ZE SCRAPERA');
    console.log('='.repeat(70));
    console.log(`📅 Data: ${date}`);
    console.log(`⚽ Sport: ${sport}`);
    console.log(`📊 Mecze: ${total_count} (kwalifikujących: ${qualified_count})`);
    console.log(`⏰ Timestamp: ${timestamp}`);
    
    if (!matches || !Array.isArray(matches)) {
      return res.status(400).json({ 
        success: false, 
        error: 'Invalid data format - matches must be an array' 
      });
    }
    
    // Zapisz mecze do bazy danych
    let saved = 0;
    let skipped = 0;
    let errors = 0;
    
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO matches (
        match_date, match_time, sport, league,
        home_team, away_team,
        home_odds, draw_odds, away_odds,
        best_home_bookmaker, best_away_bookmaker,
        bookmakers_found, all_odds,
        h2h_count, home_wins_in_h2h_last5, draws_last_5, away_wins_in_h2h,
        win_rate, h2h_last5,
        home_form_overall, away_form_overall, form_advantage,
        qualifies,
        match_url, h2h_url,
        source, scraped_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    for (const match of matches) {
      try {
        // Konwertuj JSON fields
        const bookmakers_found = match.bookmakers_found 
          ? (typeof match.bookmakers_found === 'string' ? match.bookmakers_found : JSON.stringify(match.bookmakers_found))
          : null;
        
        const all_odds = match.all_odds
          ? (typeof match.all_odds === 'string' ? match.all_odds : JSON.stringify(match.all_odds))
          : null;
        
        const h2h_last5 = match.h2h_last5
          ? (typeof match.h2h_last5 === 'string' ? match.h2h_last5 : JSON.stringify(match.h2h_last5))
          : null;
        
        const home_form = match.home_form_overall
          ? (typeof match.home_form_overall === 'string' ? match.home_form_overall : JSON.stringify(match.home_form_overall))
          : null;
        
        const away_form = match.away_form_overall
          ? (typeof match.away_form_overall === 'string' ? match.away_form_overall : JSON.stringify(match.away_form_overall))
          : null;
        
        stmt.run(
          match.match_date || date,
          match.match_time || null,
          sport,
          match.league || null,
          match.home_team,
          match.away_team,
          match.home_odds || null,
          match.draw_odds || null,
          match.away_odds || null,
          match.best_home_bookmaker || null,
          match.best_away_bookmaker || null,
          bookmakers_found,
          all_odds,
          match.h2h_count || 0,
          match.home_wins_in_h2h_last5 || 0,
          match.draws_last_5 || 0,
          match.away_wins_in_h2h || 0,
          match.win_rate || null,
          h2h_last5,
          home_form,
          away_form,
          match.form_advantage ? 1 : 0,
          match.qualifies ? 1 : 0,
          match.match_url || null,
          match.h2h_url || null,
          'github_actions',
          timestamp || new Date().toISOString()
        );
        
        saved++;
        
      } catch (err) {
        console.error(`❌ Błąd zapisywania meczu ${match.home_team} vs ${match.away_team}:`, err.message);
        errors++;
      }
    }
    
    stmt.finalize();
    
    console.log(`\n✅ Zapisano: ${saved} meczów`);
    if (errors > 0) console.log(`⚠️  Błędy: ${errors}`);
    console.log('='.repeat(70) + '\n');
    
    res.json({
      success: true,
      received: total_count,
      saved: saved,
      errors: errors,
      message: `Zapisano ${saved} meczów do bazy danych`
    });
    
  } catch (error) {
    console.error('❌ Błąd przetwarzania webhook:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error',
      details: error.message 
    });
  }
});

// ============================================================================
// ENDPOINT 3: Pobierz mecze (dla frontendu)
// ============================================================================
app.get('/api/matches', (req, res) => {
  const { sport, date, qualifies, limit = 1000 } = req.query;
  
  let query = 'SELECT * FROM matches WHERE 1=1';
  const params = [];
  
  if (sport) {
    query += ' AND sport = ?';
    params.push(sport);
  }
  
  if (date) {
    query += ' AND match_date = ?';
    params.push(date);
  }
  
  if (qualifies === 'true' || qualifies === '1') {
    query += ' AND qualifies = 1';
  }
  
  query += ' ORDER BY match_date DESC, match_time ASC LIMIT ?';
  params.push(parseInt(limit));
  
  db.all(query, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ success: false, error: err.message });
    }
    
    // Parse JSON fields
    const matches = rows.map(row => ({
      ...row,
      bookmakers_found: row.bookmakers_found ? JSON.parse(row.bookmakers_found) : [],
      all_odds: row.all_odds ? JSON.parse(row.all_odds) : {},
      h2h_last5: row.h2h_last5 ? JSON.parse(row.h2h_last5) : [],
      home_form_overall: row.home_form_overall ? JSON.parse(row.home_form_overall) : [],
      away_form_overall: row.away_form_overall ? JSON.parse(row.away_form_overall) : [],
      qualifies: row.qualifies === 1,
      form_advantage: row.form_advantage === 1
    }));
    
    res.json({
      success: true,
      matches: matches,
      count: matches.length
    });
  });
});

// ============================================================================
// ENDPOINT 4: Statystyki
// ============================================================================
app.get('/api/stats', (req, res) => {
  db.get(`
    SELECT 
      COUNT(*) as total,
      COUNT(CASE WHEN qualifies = 1 THEN 1 END) as qualified,
      COUNT(DISTINCT sport) as sports,
      COUNT(DISTINCT match_date) as dates,
      MIN(match_date) as first_date,
      MAX(match_date) as last_date,
      MAX(scraped_at) as last_update
    FROM matches
  `, (err, row) => {
    if (err) {
      return res.status(500).json({ success: false, error: err.message });
    }
    
    res.json({
      success: true,
      stats: {
        total_matches: row.total,
        qualifying_matches: row.qualified,
        unique_sports: row.sports,
        date_range: `${row.first_date} - ${row.last_date}`,
        dates: row.dates,
        last_update: row.last_update
      }
    });
  });
});

// ============================================================================
// ENDPOINT 5: Lista sportów
// ============================================================================
app.get('/api/sports', (req, res) => {
  db.all(`
    SELECT 
      sport,
      COUNT(*) as total_count,
      COUNT(CASE WHEN qualifies = 1 THEN 1 END) as qualifying_count
    FROM matches
    GROUP BY sport
    ORDER BY total_count DESC
  `, (err, rows) => {
    if (err) {
      return res.status(500).json({ success: false, error: err.message });
    }
    
    res.json({
      success: true,
      sports: rows
    });
  });
});

// ============================================================================
// Uruchom serwer
// ============================================================================
app.listen(PORT, () => {
  console.log('\n' + '='.repeat(70));
  console.log('🚀 APLIKACJA UI URUCHOMIONA');
  console.log('='.repeat(70));
  console.log(`📍 URL: http://localhost:${PORT}`);
  console.log(`📊 API: http://localhost:${PORT}/api`);
  console.log(`💾 Baza: ${DB_PATH}`);
  console.log(`🔑 API Key: ${API_KEY ? '✅ Ustawiony' : '⚠️  Brak (development mode)'}`);
  console.log('='.repeat(70));
  console.log('\n📝 Dostępne endpointy:');
  console.log('  GET  /api/health          - Health check');
  console.log('  POST /api/webhook/matches - Odbierz dane ze scrapera (wymaga API Key)');
  console.log('  GET  /api/matches         - Lista meczów (?sport=football&date=2025-10-26&qualifies=true)');
  console.log('  GET  /api/stats           - Statystyki bazy danych');
  console.log('  GET  /api/sports          - Lista sportów z licznikami');
  console.log('\n💡 Aby zatrzymać serwer: Ctrl+C\n');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Zamykanie serwera...');
  db.close((err) => {
    if (err) {
      console.error('❌ Błąd zamykania bazy:', err.message);
    } else {
      console.log('✅ Baza zamknięta');
    }
    process.exit(0);
  });
});
