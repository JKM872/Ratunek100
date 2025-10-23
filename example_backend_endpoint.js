/**
 * 📡 PRZYKŁADOWY ENDPOINT DLA TWOJEJ APLIKACJI UI
 * ==============================================
 * 
 * Ten plik pokazuje jak zaimplementować endpoint
 * do odbierania danych ze scrapera.
 * 
 * Wybierz framework który używasz i skopiuj odpowiedni kod.
 */

// ============================================
// 1. EXPRESS.JS (Node.js)
// ============================================

const express = require('express');
const cors = require('cors');
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Endpoint do odbierania meczów
app.post('/api/webhook/matches', (req, res) => {
  const { date, sport, matches, qualified_count, total_count, timestamp } = req.body;
  
  console.log(`✅ Otrzymano dane ze scrapera:`);
  console.log(`   Data: ${date}`);
  console.log(`   Sport: ${sport}`);
  console.log(`   Mecze: ${total_count} (kwalifikujących: ${qualified_count})`);
  console.log(`   Timestamp: ${timestamp}`);
  
  // ===== TUTAJ DODAJ SWOJĄ LOGIKĘ =====
  
  // Przykład 1: Zapisz do bazy danych (MongoDB)
  // db.collection('matches').insertMany(matches);
  
  // Przykład 2: Zapisz do bazy danych (PostgreSQL)
  // await prisma.match.createMany({ data: matches });
  
  // Przykład 3: Zapisz do pliku (dla testów)
  // const fs = require('fs');
  // fs.writeFileSync(`matches_${date}_${sport}.json`, JSON.stringify(matches, null, 2));
  
  // Przykład 4: Powiadom frontend przez WebSocket
  // io.emit('matches-updated', { date, sport, count: qualified_count });
  
  // Przykład 5: Wyślij powiadomienie push
  // await sendPushNotification(`Nowe mecze: ${qualified_count} kwalifikujących się!`);
  
  // ===== KONIEC TWOJEJ LOGIKI =====
  
  // Odpowiedź (ważne!)
  res.status(200).json({
    status: 'success',
    received: matches.length,
    qualified: qualified_count,
    message: `Zapisano ${qualified_count} kwalifikujących się meczów`
  });
});

// Health check endpoint (opcjonalny, ale zalecany)
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Uruchom serwer
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});


// ============================================
// 2. NEXT.JS API ROUTE
// ============================================

// File: app/api/webhook/matches/route.ts
// lub: pages/api/webhook/matches.ts (stary routing)

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    
    const { date, sport, matches, qualified_count } = data;
    
    console.log(`✅ Otrzymano ${matches.length} meczów (${sport})`);
    
    // ===== TUTAJ DODAJ SWOJĄ LOGIKĘ =====
    
    // Przykład z Prisma
    // await prisma.match.createMany({
    //   data: matches.map(m => ({
    //     url: m.match_url,
    //     homeTeam: m.home_team,
    //     awayTeam: m.away_team,
    //     matchTime: m.match_time,
    //     homeWins: m.home_wins_in_h2h_last5,
    //     qualifies: m.qualifies,
    //     sport: sport,
    //     date: new Date(date)
    //   }))
    // });
    
    // Revalidate cache (Next.js)
    // revalidatePath('/matches');
    
    // ===== KONIEC TWOJEJ LOGIKI =====
    
    return NextResponse.json({
      success: true,
      received: matches.length,
      qualified: qualified_count
    });
    
  } catch (error) {
    console.error('❌ Błąd:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}


// ============================================
// 3. FASTAPI (Python)
// ============================================

/*
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchesWebhook(BaseModel):
    date: str
    sport: str
    matches: List[Dict[str, Any]]
    qualified_count: int
    total_count: int
    timestamp: str

@app.post("/api/webhook/matches")
async def receive_matches(data: MatchesWebhook):
    print(f"✅ Otrzymano {len(data.matches)} meczów ({data.sport})")
    
    # ===== TUTAJ DODAJ SWOJĄ LOGIKĘ =====
    
    # Przykład z SQLAlchemy
    # for match in data.matches:
    #     db_match = Match(**match)
    #     db.add(db_match)
    # db.commit()
    
    # ===== KONIEC TWOJEJ LOGIKI =====
    
    return {
        "status": "success",
        "received": len(data.matches),
        "qualified": data.qualified_count
    }

@app.get("/api/health")
async def health():
    return {"status": "OK", "timestamp": datetime.now().isoformat()}

# Uruchom: uvicorn main:app --reload
*/


// ============================================
// 4. FLASK (Python)
// ============================================

/*
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/webhook/matches', methods=['POST'])
def receive_matches():
    data = request.get_json()
    
    date = data.get('date')
    sport = data.get('sport')
    matches = data.get('matches', [])
    qualified_count = data.get('qualified_count', 0)
    
    print(f"✅ Otrzymano {len(matches)} meczów ({sport})")
    
    # ===== TUTAJ DODAJ SWOJĄ LOGIKĘ =====
    
    # Przykład zapisu do bazy
    # for match in matches:
    #     db.session.add(Match(**match))
    # db.session.commit()
    
    # ===== KONIEC TWOJEJ LOGIKI =====
    
    return jsonify({
        'status': 'success',
        'received': len(matches),
        'qualified': qualified_count
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    app.run(port=3000, debug=True)
*/


// ============================================
// 5. PRZYKŁAD Z WEBSOCKET (real-time updates)
// ============================================

const express = require('express');
const http = require('http');
const socketIO = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
  cors: { origin: "*" }
});

app.use(express.json());

// Endpoint z WebSocket notification
app.post('/api/webhook/matches', (req, res) => {
  const { date, sport, matches, qualified_count } = req.body;
  
  console.log(`✅ Otrzymano ${matches.length} meczów (${sport})`);
  
  // Zapisz do bazy
  // ...
  
  // Powiadom wszystkich klientów przez WebSocket
  io.emit('matches-updated', {
    date,
    sport,
    matches,
    qualified_count,
    timestamp: new Date().toISOString()
  });
  
  res.json({ status: 'success', received: matches.length });
});

// WebSocket connection
io.on('connection', (socket) => {
  console.log('👤 Klient połączony');
  
  socket.on('disconnect', () => {
    console.log('👋 Klient rozłączony');
  });
});

server.listen(3000, () => {
  console.log('🚀 Server with WebSocket on http://localhost:3000');
});


// ============================================
// 6. PRZYKŁAD FRONTENDU (React)
// ============================================

/*
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

function MatchesDashboard() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Połącz z WebSocket
    const socket = io('http://localhost:3000');
    
    socket.on('matches-updated', (data) => {
      console.log(`✅ Nowe mecze: ${data.qualified_count}`);
      
      // Aktualizuj state
      setMatches(prevMatches => [...data.matches, ...prevMatches]);
      
      // Pokaż notyfikację
      showNotification(`Nowe mecze: ${data.qualified_count} kwalifikujących się!`);
    });
    
    // Wczytaj istniejące mecze przy starcie
    fetchMatches();
    
    return () => socket.disconnect();
  }, []);
  
  async function fetchMatches() {
    setLoading(true);
    const response = await fetch('/api/matches');
    const data = await response.json();
    setMatches(data.matches);
    setLoading(false);
  }
  
  if (loading) return <div>Ładowanie...</div>;
  
  return (
    <div>
      <h1>Mecze ({matches.length})</h1>
      {matches.map(match => (
        <MatchCard key={match.match_url} {...match} />
      ))}
    </div>
  );
}

function MatchCard({ home_team, away_team, match_time, home_wins, qualifies }) {
  return (
    <div className={qualifies ? 'match qualified' : 'match'}>
      <div className="teams">
        {home_team} vs {away_team}
      </div>
      <div className="time">{match_time}</div>
      <div className="stats">
        H2H: {home_wins}/5 wygranych gospodarzy
      </div>
      {qualifies && <span className="badge">✅ Kwalifikuje się</span>}
    </div>
  );
}
*/


// ============================================
// 7. PRZYKŁAD Z BAZĄ DANYCH (Prisma)
// ============================================

/*
// schema.prisma
model Match {
  id           Int      @id @default(autoincrement())
  matchUrl     String   @unique
  homeTeam     String
  awayTeam     String
  matchTime    String
  homeWins     Int
  qualifies    Boolean
  sport        String
  date         DateTime
  homeOdds     Float?
  awayOdds     Float?
  createdAt    DateTime @default(now())
}

// API endpoint
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

app.post('/api/webhook/matches', async (req, res) => {
  const { matches, date, sport } = req.body;
  
  try {
    // Zapisz do bazy
    await prisma.match.createMany({
      data: matches.map(m => ({
        matchUrl: m.match_url,
        homeTeam: m.home_team,
        awayTeam: m.away_team,
        matchTime: m.match_time,
        homeWins: m.home_wins_in_h2h_last5,
        qualifies: m.qualifies,
        sport: sport,
        date: new Date(date),
        homeOdds: m.home_odds,
        awayOdds: m.away_odds
      })),
      skipDuplicates: true // Nie duplikuj meczów
    });
    
    res.json({ status: 'success' });
  } catch (error) {
    console.error('Błąd zapisu:', error);
    res.status(500).json({ error: 'Database error' });
  }
});
*/


// ============================================
// 8. BEZPIECZEŃSTWO - API KEY
// ============================================

// Middleware sprawdzający API key
function validateApiKey(req, res, next) {
  const apiKey = req.headers['authorization'];
  const expectedKey = process.env.API_KEY || 'your-secret-key';
  
  if (!apiKey || apiKey !== `Bearer ${expectedKey}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  next();
}

// Użycie
app.post('/api/webhook/matches', validateApiKey, (req, res) => {
  // Endpoint zabezpieczony API key
  // ...
});


// ============================================
// 9. LOGGING I MONITORING
// ============================================

const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'matches.log' })
  ]
});

app.post('/api/webhook/matches', (req, res) => {
  const { date, sport, qualified_count } = req.body;
  
  // Loguj każde otrzymanie danych
  logger.info('Received matches', {
    date,
    sport,
    qualified_count,
    timestamp: new Date().toISOString()
  });
  
  // ... reszta logiki
});


// ============================================
// 10. RATE LIMITING (ochrona przed spamem)
// ============================================

const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minut
  max: 100 // max 100 requestów na 15 minut
});

app.use('/api/webhook', limiter);

module.exports = app;







