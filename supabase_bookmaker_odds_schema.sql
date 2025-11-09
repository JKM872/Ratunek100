-- ============================================================================
-- Tabela dla kursów bukmacherskich pobranych lokalnie (Polska)
-- ============================================================================
-- PROBLEM: GitHub Actions (USA) nie ma dostępu do polskich bukmacherów
-- ROZWIĄZANIE: Lokalny scraper (Polska) → Supabase → GitHub Actions odczytuje
-- ============================================================================

-- Usuń tabelę jeśli istnieje (tylko dla dev)
DROP TABLE IF EXISTS bookmaker_odds CASCADE;

-- Utwórz tabelę
CREATE TABLE bookmaker_odds (
    id BIGSERIAL PRIMARY KEY,
    
    -- Klucz meczu (normalizowany)
    match_key TEXT NOT NULL,
    -- Format: "home_team_vs_away_team" (lowercase, bez polskich znaków)
    -- Example: "legia_warszawa_vs_lech_poznan"
    
    -- Data meczu
    match_date DATE NOT NULL,
    
    -- Kursy w formacie JSON
    -- {
    --   "fortuna": {"home_odds": 2.10, "away_odds": 1.65, "draw_odds": 3.20},
    --   "superbet": {"home_odds": 2.05, "away_odds": 1.70, "draw_odds": 3.10},
    --   "sts": {"home_odds": 2.15, "away_odds": 1.60, "draw_odds": 3.25}
    -- }
    bookmakers JSONB NOT NULL,
    
    -- Metadane
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Źródło danych (local_polish_scraper, api_fallback, etc.)
    source TEXT DEFAULT 'local_polish_scraper',
    
    -- Sport (football, basketball, volleyball, etc.)
    sport TEXT DEFAULT 'football',
    
    -- Nazwa drużyn (oryginalne, dla debugowania)
    home_team_original TEXT,
    away_team_original TEXT,
    
    -- Liczba dostępnych bukmacherów (dla quick filtering)
    bookmakers_count INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- UNIQUE constraint na match_key + match_date
    CONSTRAINT unique_match_key_date UNIQUE (match_key, match_date)
);

-- ============================================================================
-- Indeksy dla szybkiego wyszukiwania
-- ============================================================================

-- Główny indeks - wyszukiwanie po kluczu meczu i dacie
CREATE INDEX idx_bookmaker_odds_match_key_date 
ON bookmaker_odds(match_key, match_date DESC);

-- Wyszukiwanie po dacie (dzisiejsze mecze)
CREATE INDEX idx_bookmaker_odds_match_date 
ON bookmaker_odds(match_date DESC);

-- Wyszukiwanie po sporcie
CREATE INDEX idx_bookmaker_odds_sport 
ON bookmaker_odds(sport);

-- GIN index na JSON dla zaawansowanych zapytań
CREATE INDEX idx_bookmaker_odds_bookmakers_gin 
ON bookmaker_odds USING GIN (bookmakers);

-- Wyszukiwanie aktywnych rekordów
CREATE INDEX idx_bookmaker_odds_active 
ON bookmaker_odds(is_active) WHERE is_active = TRUE;

-- ============================================================================
-- Funkcje pomocnicze
-- ============================================================================

-- Funkcja do normalizacji nazw drużyn (usuwa polskie znaki, lowercase)
CREATE OR REPLACE FUNCTION normalize_team_name(team_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(
                                        REPLACE(team_name, 'ą', 'a'),
                                    'ć', 'c'),
                                'ę', 'e'),
                            'ł', 'l'),
                        'ń', 'n'),
                    'ó', 'o'),
                'ś', 's'),
            'ź', 'z'),
        'ż', 'z')
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Funkcja do generowania match_key
CREATE OR REPLACE FUNCTION generate_match_key(home_team TEXT, away_team TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN normalize_team_name(home_team) || '_vs_' || normalize_team_name(away_team);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Trigger do automatycznego update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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
