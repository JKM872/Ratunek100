-- ============================================================================-- ============================================================================

-- SUPABASE BOOKMAKER_ODDS TABLE SCHEMA-- Tabela dla kursów bukmacherskich pobranych lokalnie (Polska)

-- ============================================================================-- ============================================================================

-- Table for storing Polish bookmaker odds (Fortuna, Superbet, STS)-- PROBLEM: GitHub Actions (USA) nie ma dostępu do polskich bukmacherów

-- Scraped by local_bookmaker_scraper.py running on Poland IP-- ROZWIĄZANIE: Lokalny scraper (Polska) → Supabase → GitHub Actions odczytuje

-- Accessed globally by backend API and frontend-- ============================================================================



CREATE TABLE IF NOT EXISTS bookmaker_odds (-- Usuń tabelę jeśli istnieje (tylko dla dev)

  id BIGSERIAL PRIMARY KEY,DROP TABLE IF EXISTS bookmaker_odds CASCADE;

  

  -- Match identification-- Utwórz tabelę

  match_key TEXT NOT NULL,              -- Normalized key: "home_vs_away_2025-01-15"CREATE TABLE bookmaker_odds (

  home_team TEXT NOT NULL,              -- Original team name from bookmaker    id BIGSERIAL PRIMARY KEY,

  away_team TEXT NOT NULL,              -- Original team name from bookmaker    

  match_date DATE NOT NULL,             -- Match date (YYYY-MM-DD)    -- Klucz meczu (normalizowany)

      match_key TEXT NOT NULL,

  -- Bookmaker information    -- Format: "home_team_vs_away_team" (lowercase, bez polskich znaków)

  bookmaker TEXT NOT NULL,              -- "Fortuna", "Superbet", or "STS"    -- Example: "legia_warszawa_vs_lech_poznan"

      

  -- Odds    -- Data meczu

  home_odds DECIMAL(6,2),               -- Home win odds (e.g., 1.85)    match_date DATE NOT NULL,

  draw_odds DECIMAL(6,2),               -- Draw odds (NULL for sports without draw)    

  away_odds DECIMAL(6,2),               -- Away win odds (e.g., 2.10)    -- Kursy w formacie JSON

      -- {

  -- Timestamps    --   "fortuna": {"home_odds": 2.10, "away_odds": 1.65, "draw_odds": 3.20},

  created_at TIMESTAMPTZ DEFAULT NOW(),    --   "superbet": {"home_odds": 2.05, "away_odds": 1.70, "draw_odds": 3.10},

  updated_at TIMESTAMPTZ DEFAULT NOW(),    --   "sts": {"home_odds": 2.15, "away_odds": 1.60, "draw_odds": 3.25}

      -- }

  -- Constraints    bookmakers JSONB NOT NULL,

  CONSTRAINT unique_match_bookmaker UNIQUE (match_key, bookmaker, match_date)    

);    -- Metadane

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

-- ============================================================================    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

-- INDEXES for performance    

-- ============================================================================    -- Źródło danych (local_polish_scraper, api_fallback, etc.)

    source TEXT DEFAULT 'local_polish_scraper',

-- Index for fast match_key lookups    

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_match_key     -- Sport (football, basketball, volleyball, etc.)

ON bookmaker_odds(match_key);    sport TEXT DEFAULT 'football',

    

-- Index for date-based queries    -- Nazwa drużyn (oryginalne, dla debugowania)

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_date     home_team_original TEXT,

ON bookmaker_odds(match_date);    away_team_original TEXT,

    

-- Index for bookmaker filtering    -- Liczba dostępnych bukmacherów (dla quick filtering)

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_bookmaker     bookmakers_count INTEGER DEFAULT 0,

ON bookmaker_odds(bookmaker);    

    -- Status

-- Composite index for common query pattern (match_key + date)    is_active BOOLEAN DEFAULT TRUE,

CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_match_date     

ON bookmaker_odds(match_key, match_date);    -- UNIQUE constraint na match_key + match_date

    CONSTRAINT unique_match_key_date UNIQUE (match_key, match_date)

-- ============================================================================);

-- ROW LEVEL SECURITY (RLS)

-- ============================================================================-- ============================================================================

-- Enable RLS for security-- Indeksy dla szybkiego wyszukiwania

ALTER TABLE bookmaker_odds ENABLE ROW LEVEL SECURITY;-- ============================================================================



-- Policy: Allow public read access (for API)-- Główny indeks - wyszukiwanie po kluczu meczu i dacie

CREATE POLICY "Allow public read access"CREATE INDEX idx_bookmaker_odds_match_key_date 

ON bookmaker_odds FOR SELECTON bookmaker_odds(match_key, match_date DESC);

TO public

USING (true);-- Wyszukiwanie po dacie (dzisiejsze mecze)

CREATE INDEX idx_bookmaker_odds_match_date 

-- Policy: Allow authenticated insert (for scraper with service_role key)ON bookmaker_odds(match_date DESC);

CREATE POLICY "Allow authenticated insert"

ON bookmaker_odds FOR INSERT-- Wyszukiwanie po sporcie

TO authenticatedCREATE INDEX idx_bookmaker_odds_sport 

WITH CHECK (true);ON bookmaker_odds(sport);



-- Policy: Allow authenticated update (for scraper with service_role key)-- GIN index na JSON dla zaawansowanych zapytań

CREATE POLICY "Allow authenticated update"CREATE INDEX idx_bookmaker_odds_bookmakers_gin 

ON bookmaker_odds FOR UPDATEON bookmaker_odds USING GIN (bookmakers);

TO authenticated

USING (true)-- Wyszukiwanie aktywnych rekordów

WITH CHECK (true);CREATE INDEX idx_bookmaker_odds_active 

ON bookmaker_odds(is_active) WHERE is_active = TRUE;

-- ============================================================================

-- TRIGGER for updated_at timestamp-- ============================================================================

-- ============================================================================-- Funkcje pomocnicze

CREATE OR REPLACE FUNCTION update_bookmaker_odds_updated_at()-- ============================================================================

RETURNS TRIGGER AS $$

BEGIN-- Funkcja do normalizacji nazw drużyn (usuwa polskie znaki, lowercase)

  NEW.updated_at = NOW();CREATE OR REPLACE FUNCTION normalize_team_name(team_name TEXT)

  RETURN NEW;RETURNS TEXT AS $$

END;BEGIN

$$ LANGUAGE plpgsql;    RETURN LOWER(

        REPLACE(

CREATE TRIGGER trigger_update_bookmaker_odds_updated_at            REPLACE(

BEFORE UPDATE ON bookmaker_odds                REPLACE(

FOR EACH ROW                    REPLACE(

EXECUTE FUNCTION update_bookmaker_odds_updated_at();                        REPLACE(

                            REPLACE(

-- ============================================================================                                REPLACE(

-- EXAMPLE DATA (for testing)                                    REPLACE(

-- ============================================================================                                        REPLACE(team_name, 'ą', 'a'),

/*                                    'ć', 'c'),

INSERT INTO bookmaker_odds (match_key, home_team, away_team, match_date, bookmaker, home_odds, draw_odds, away_odds)                                'ę', 'e'),

VALUES                             'ł', 'l'),

  ('legia_warszawa_vs_rakow_czestochowa_2025-01-15', 'Legia Warszawa', 'Raków Częstochowa', '2025-01-15', 'Fortuna', 1.75, 3.40, 4.20),                        'ń', 'n'),

  ('legia_warszawa_vs_rakow_czestochowa_2025-01-15', 'Legia Warszawa', 'Raków Częstochowa', '2025-01-15', 'Superbet', 1.80, 3.35, 4.10),                    'ó', 'o'),

  ('legia_warszawa_vs_rakow_czestochowa_2025-01-15', 'Legia Warszawa', 'Raków Częstochowa', '2025-01-15', 'STS', 1.78, 3.30, 4.15);                'ś', 's'),

*/            'ź', 'z'),

        'ż', 'z')

-- ============================================================================    );

-- USEFUL QUERIESEND;

-- ============================================================================$$ LANGUAGE plpgsql IMMUTABLE;



-- Get all odds for a match-- Funkcja do generowania match_key

-- SELECT * FROM bookmaker_odds CREATE OR REPLACE FUNCTION generate_match_key(home_team TEXT, away_team TEXT)

-- WHERE match_key = 'legia_warszawa_vs_rakow_czestochowa_2025-01-15' RETURNS TEXT AS $$

-- ORDER BY bookmaker;BEGIN

    RETURN normalize_team_name(home_team) || '_vs_' || normalize_team_name(away_team);

-- Get today's matches with odds countEND;

-- SELECT match_key, home_team, away_team, COUNT(*) as bookmaker_count$$ LANGUAGE plpgsql IMMUTABLE;

-- FROM bookmaker_odds

-- WHERE match_date = CURRENT_DATE-- Trigger do automatycznego update updated_at

-- GROUP BY match_key, home_team, away_teamCREATE OR REPLACE FUNCTION update_updated_at_column()

-- ORDER BY bookmaker_count DESC;RETURNS TRIGGER AS $$

BEGIN

-- Get statistics by bookmaker    NEW.updated_at = NOW();

-- SELECT bookmaker, COUNT(*) as match_count    RETURN NEW;

-- FROM bookmaker_oddsEND;

-- WHERE match_date = CURRENT_DATE$$ LANGUAGE plpgsql;

-- GROUP BY bookmaker;

CREATE TRIGGER update_bookmaker_odds_updated_at
    BEFORE UPDATE ON bookmaker_odds
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger do automatycznego liczenia bookmakers_count
CREATE OR REPLACE FUNCTION update_bookmakers_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.bookmakers_count = (
        SELECT COUNT(*)
        FROM jsonb_object_keys(NEW.bookmakers)
        WHERE NEW.bookmakers->jsonb_object_keys.key IS NOT NULL
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bookmaker_odds_count
    BEFORE INSERT OR UPDATE OF bookmakers ON bookmaker_odds
    FOR EACH ROW
    EXECUTE FUNCTION update_bookmakers_count();

-- ============================================================================
-- RLS (Row Level Security) - opcjonalne, dla bezpieczeństwa
-- ============================================================================

-- Włącz RLS
ALTER TABLE bookmaker_odds ENABLE ROW LEVEL SECURITY;

-- Policy: SELECT (odczyt) - wszyscy mogą czytać aktywne rekordy
CREATE POLICY "Allow public read access to active odds"
    ON bookmaker_odds
    FOR SELECT
    USING (is_active = TRUE);

-- Policy: INSERT/UPDATE - tylko z autoryzacją (service_role key)
CREATE POLICY "Allow insert with service role"
    ON bookmaker_odds
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow update with service role"
    ON bookmaker_odds
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- Przykładowe zapytania (komentarze dla dokumentacji)
-- ============================================================================

-- Pobierz kursy dla konkretnego meczu
/*
SELECT bookmakers
FROM bookmaker_odds
WHERE match_key = 'legia_warszawa_vs_lech_poznan'
  AND match_date = CURRENT_DATE
  AND is_active = TRUE
ORDER BY created_at DESC
LIMIT 1;
*/

-- Pobierz wszystkie dzisiejsze mecze z kursami
/*
SELECT 
    match_key,
    home_team_original,
    away_team_original,
    bookmakers,
    bookmakers_count,
    created_at
FROM bookmaker_odds
WHERE match_date = CURRENT_DATE
  AND is_active = TRUE
  AND bookmakers_count >= 2  -- Minimum 2 bukmacherów
ORDER BY created_at DESC;
*/

-- Sprawdź dostępność konkretnego bukmachera
/*
SELECT 
    match_key,
    bookmakers->'fortuna' as fortuna_odds,
    bookmakers->'superbet' as superbet_odds,
    bookmakers->'sts' as sts_odds
FROM bookmaker_odds
WHERE match_date = CURRENT_DATE
  AND bookmakers ? 'fortuna'  -- Ma Fortuna
  AND is_active = TRUE;
*/

-- Statystyki bukmacherów
/*
SELECT 
    COUNT(*) as total_matches,
    COUNT(*) FILTER (WHERE bookmakers ? 'fortuna') as with_fortuna,
    COUNT(*) FILTER (WHERE bookmakers ? 'superbet') as with_superbet,
    COUNT(*) FILTER (WHERE bookmakers ? 'sts') as with_sts,
    AVG(bookmakers_count) as avg_bookmakers_per_match
FROM bookmaker_odds
WHERE match_date = CURRENT_DATE
  AND is_active = TRUE;
*/

-- ============================================================================
-- Testowe dane (dla rozwoju)
-- ============================================================================

-- Przykład: Dodaj testowy mecz
/*
INSERT INTO bookmaker_odds (
    match_key,
    match_date,
    home_team_original,
    away_team_original,
    bookmakers,
    sport
) VALUES (
    'legia_warszawa_vs_lech_poznan',
    CURRENT_DATE,
    'Legia Warszawa',
    'Lech Poznań',
    '{
        "fortuna": {"home_odds": 2.10, "away_odds": 1.65, "draw_odds": 3.20},
        "superbet": {"home_odds": 2.05, "away_odds": 1.70, "draw_odds": 3.10},
        "sts": {"home_odds": 2.15, "away_odds": 1.60, "draw_odds": 3.25}
    }'::jsonb,
    'football'
) ON CONFLICT (match_key, match_date) DO UPDATE SET
    bookmakers = EXCLUDED.bookmakers,
    updated_at = NOW();
*/

-- ============================================================================
-- Cleanup (automatyczne czyszczenie starych danych)
-- ============================================================================

-- Funkcja do czyszczenia starych rekordów (>30 dni)
CREATE OR REPLACE FUNCTION cleanup_old_bookmaker_odds()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM bookmaker_odds
    WHERE match_date < CURRENT_DATE - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Komentarz: Możesz uruchomić to cron jobem w Supabase:
-- SELECT cron.schedule('cleanup-old-odds', '0 2 * * *', 'SELECT cleanup_old_bookmaker_odds();');

-- ============================================================================
--Grantowanie uprawnień (opcjonalne, zależnie od setup)
-- ============================================================================

-- Grant do service_role (dla zapisów z local scraper)
-- GRANT ALL ON bookmaker_odds TO service_role;
-- GRANT USAGE, SELECT ON SEQUENCE bookmaker_odds_id_seq TO service_role;

-- Grant do anon (dla odczytów z GitHub Actions)
-- GRANT SELECT ON bookmaker_odds TO anon;

-- ============================================================================
-- DONE! Tabela gotowa do użycia
-- ============================================================================

COMMENT ON TABLE bookmaker_odds IS 'Kursy bukmacherskie pobrane lokalnie (Polska IP) dla GitHub Actions';
COMMENT ON COLUMN bookmaker_odds.match_key IS 'Normalized match identifier: home_vs_away (lowercase, no polish chars)';
COMMENT ON COLUMN bookmaker_odds.bookmakers IS 'JSON with odds from Fortuna, Superbet, STS';
COMMENT ON COLUMN bookmaker_odds.source IS 'Data source: local_polish_scraper, api_fallback, manual';
