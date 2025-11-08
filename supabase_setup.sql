-- ============================================
-- SUPABASE DATABASE SETUP
-- ============================================
-- Run this in Supabase SQL Editor:
-- https://supabase.com/dashboard/project/bfslhqnxsgmdyptrqshj/sql/new
-- ============================================

-- Create matches table with all required fields
CREATE TABLE IF NOT EXISTS matches (
  id BIGSERIAL PRIMARY KEY,
  sport TEXT,
  match_date TEXT,
  match_time TEXT,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  home_odds FLOAT,
  away_odds FLOAT,
  draw_odds FLOAT,
  home_win_percentage FLOAT,
  draw_percentage FLOAT,
  away_win_percentage FLOAT,
  avg_home_goals FLOAT,
  avg_away_goals FLOAT,
  qualifies INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  all_odds JSONB,
  bookmaker_name TEXT,
  bookmaker_url TEXT,
  
  -- UNIQUE constraint to prevent duplicates
  UNIQUE(sport, home_team, away_team, match_time)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_matches_sport ON matches(sport);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_qualifies ON matches(qualifies);
CREATE INDEX IF NOT EXISTS idx_matches_created_at ON matches(created_at DESC);

-- Enable Row Level Security (RLS) but allow all operations for now
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust later for security)
CREATE POLICY "Allow all operations on matches" 
ON matches 
FOR ALL 
USING (true) 
WITH CHECK (true);

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'matches'
ORDER BY ordinal_position;

-- Check indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'matches';

-- Check row count (should be 0 initially)
SELECT COUNT(*) as total_matches FROM matches;

-- ============================================
-- DONE!
-- ============================================
-- ✅ Table created with UNIQUE constraint
-- ✅ Indexes added for performance
-- ✅ RLS enabled with permissive policy
-- ✅ Ready for data from scraper
-- ============================================
