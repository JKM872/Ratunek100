/**
 * 🧪 TEST WEBHOOK - Testuj połączenie scrapera z aplikacją UI
 */

const API_URL = process.env.API_URL || 'http://localhost:3001';  // Zmieniony na 3001
const API_KEY = process.env.SCRAPER_API_KEY || 'super-secret-key-12345';

// Przykładowe dane (symulacja scrapera)
const testData = {
  date: '2025-10-26',
  sport: 'football',
  qualified_count: 2,
  total_count: 3,
  timestamp: new Date().toISOString(),
  source: 'test_script',
  matches: [
    {
      match_date: '2025-10-26',
      match_time: '20:00',
      home_team: 'Real Madrid',
      away_team: 'Barcelona',
      league: 'La Liga',
      home_odds: 2.15,
      draw_odds: 3.40,
      away_odds: 3.10,
      best_home_bookmaker: 'STS',
      best_away_bookmaker: 'Fortuna',
      bookmakers_found: ['STS', 'Fortuna', 'Superbet'],
      all_odds: {
        'STS': { home: 2.15, draw: 3.40, away: 3.10 },
        'Fortuna': { home: 2.10, draw: 3.50, away: 3.20 },
        'Superbet': { home: 2.20, draw: 3.30, away: 3.00 }
      },
      h2h_count: 10,
      home_wins_in_h2h_last5: 3,
      draws_last_5: 1,
      away_wins_in_h2h: 1,
      win_rate: 0.7,
      h2h_last5: ['W', 'W', 'D', 'W', 'L'],
      home_form_overall: ['W', 'W', 'W', 'D', 'W'],
      away_form_overall: ['L', 'W', 'W', 'L', 'D'],
      form_advantage: true,
      qualifies: true,
      match_url: 'https://www.flashscore.pl/mecz/example1',
      h2h_url: 'https://www.flashscore.pl/h2h/example1'
    },
    {
      match_date: '2025-10-26',
      match_time: '18:00',
      home_team: 'Manchester United',
      away_team: 'Liverpool',
      league: 'Premier League',
      home_odds: 2.80,
      draw_odds: 3.20,
      away_odds: 2.50,
      best_home_bookmaker: 'Bet365',
      best_away_bookmaker: 'STS',
      bookmakers_found: ['STS', 'Bet365'],
      all_odds: {
        'STS': { home: 2.75, draw: 3.25, away: 2.50 },
        'Bet365': { home: 2.80, draw: 3.20, away: 2.45 }
      },
      h2h_count: 8,
      home_wins_in_h2h_last5: 4,
      draws_last_5: 0,
      away_wins_in_h2h: 1,
      win_rate: 0.8,
      h2h_last5: ['W', 'W', 'W', 'L', 'W'],
      home_form_overall: ['W', 'W', 'D', 'W', 'W'],
      away_form_overall: ['W', 'L', 'W', 'W', 'L'],
      form_advantage: false,
      qualifies: true,
      match_url: 'https://www.flashscore.pl/mecz/example2',
      h2h_url: 'https://www.flashscore.pl/h2h/example2'
    },
    {
      match_date: '2025-10-26',
      match_time: '15:00',
      home_team: 'Legia Warszawa',
      away_team: 'Lech Poznań',
      league: 'Ekstraklasa',
      home_odds: 1.85,
      draw_odds: 3.60,
      away_odds: 4.20,
      best_home_bookmaker: 'STS',
      best_away_bookmaker: 'Fortuna',
      bookmakers_found: ['STS', 'Fortuna'],
      all_odds: {
        'STS': { home: 1.85, draw: 3.60, away: 4.20 },
        'Fortuna': { home: 1.80, draw: 3.70, away: 4.30 }
      },
      h2h_count: 5,
      home_wins_in_h2h_last5: 2,
      draws_last_5: 2,
      away_wins_in_h2h: 1,
      win_rate: 0.4,
      h2h_last5: ['D', 'W', 'L', 'D', 'W'],
      home_form_overall: ['W', 'D', 'W', 'L', 'W'],
      away_form_overall: ['L', 'D', 'W', 'W', 'L'],
      form_advantage: false,
      qualifies: false,
      match_url: 'https://www.flashscore.pl/mecz/example3',
      h2h_url: 'https://www.flashscore.pl/h2h/example3'
    }
  ]
};

async function testHealthCheck() {
  console.log('\n🔍 TEST 1: Health Check');
  console.log('='.repeat(60));
  
  try {
    const response = await fetch(`${API_URL}/api/health`);
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Aplikacja działa!');
      console.log('   Status:', data.status);
      console.log('   Message:', data.message);
      console.log('   Timestamp:', data.timestamp);
      return true;
    } else {
      console.log('❌ Błąd health check:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ Błąd połączenia:', error.message);
    console.log('💡 Upewnij się że aplikacja działa: node server.js');
    return false;
  }
}

async function testWebhook() {
  console.log('\n📤 TEST 2: Webhook (Wysyłka danych)');
  console.log('='.repeat(60));
  
  try {
    const response = await fetch(`${API_URL}/api/webhook/matches`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify(testData)
    });
    
    const data = await response.json();
    
    if (response.ok && data.success) {
      console.log('✅ Webhook działa!');
      console.log('   Otrzymane mecze:', data.received);
      console.log('   Zapisane mecze:', data.saved);
      console.log('   Błędy:', data.errors || 0);
      console.log('   Message:', data.message);
      return true;
    } else {
      console.log('❌ Błąd webhook:', response.status);
      console.log('   Odpowiedź:', data);
      return false;
    }
  } catch (error) {
    console.log('❌ Błąd wysyłki:', error.message);
    return false;
  }
}

async function testGetMatches() {
  console.log('\n📊 TEST 3: Pobieranie meczów (API)');
  console.log('='.repeat(60));
  
  try {
    const response = await fetch(`${API_URL}/api/matches?qualifies=true`);
    const data = await response.json();
    
    if (response.ok && data.success) {
      console.log('✅ API działa!');
      console.log('   Liczba meczów:', data.count);
      
      if (data.matches.length > 0) {
        console.log('\n   Przykładowy mecz:');
        const match = data.matches[0];
        console.log(`   ${match.home_team} vs ${match.away_team}`);
        console.log(`   Kursy: ${match.home_odds} / ${match.draw_odds} / ${match.away_odds}`);
        console.log(`   Sport: ${match.sport}`);
        console.log(`   Data: ${match.match_date} ${match.match_time || ''}`);
      }
      
      return true;
    } else {
      console.log('❌ Błąd API:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ Błąd pobierania:', error.message);
    return false;
  }
}

async function testStats() {
  console.log('\n📈 TEST 4: Statystyki');
  console.log('='.repeat(60));
  
  try {
    const response = await fetch(`${API_URL}/api/stats`);
    const data = await response.json();
    
    if (response.ok && data.success) {
      console.log('✅ Statystyki:');
      const stats = data.stats;
      console.log(`   Wszystkich meczów: ${stats.total_matches}`);
      console.log(`   Kwalifikujących się: ${stats.qualifying_matches}`);
      console.log(`   Sportów: ${stats.unique_sports}`);
      console.log(`   Zakres dat: ${stats.date_range}`);
      console.log(`   Ostatnia aktualizacja: ${stats.last_update}`);
      return true;
    } else {
      console.log('❌ Błąd statystyk:', response.status);
      return false;
    }
  } catch (error) {
    console.log('❌ Błąd:', error.message);
    return false;
  }
}

async function runTests() {
  console.log('\n' + '='.repeat(60));
  console.log('🧪 TESTY INTEGRACJI SCRAPER → UI APP');
  console.log('='.repeat(60));
  console.log(`🌐 URL: ${API_URL}`);
  console.log(`🔑 API Key: ${API_KEY}`);
  
  const results = {
    healthCheck: await testHealthCheck(),
    webhook: false,
    getMatches: false,
    stats: false
  };
  
  if (results.healthCheck) {
    results.webhook = await testWebhook();
    results.getMatches = await testGetMatches();
    results.stats = await testStats();
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('📋 PODSUMOWANIE TESTÓW');
  console.log('='.repeat(60));
  console.log(`Health Check: ${results.healthCheck ? '✅' : '❌'}`);
  console.log(`Webhook:      ${results.webhook ? '✅' : '❌'}`);
  console.log(`Get Matches:  ${results.getMatches ? '✅' : '❌'}`);
  console.log(`Stats:        ${results.stats ? '✅' : '❌'}`);
  
  const allPassed = Object.values(results).every(r => r);
  
  if (allPassed) {
    console.log('\n🎉 WSZYSTKIE TESTY PRZESZŁY!');
    console.log('💡 Możesz teraz skonfigurować GitHub Actions');
  } else {
    console.log('\n⚠️  NIEKTÓRE TESTY NIE PRZESZŁY');
    console.log('💡 Sprawdź logi serwera i spróbuj ponownie');
  }
  
  console.log('='.repeat(60) + '\n');
  
  process.exit(allPassed ? 0 : 1);
}

// Uruchom testy
runTests();
