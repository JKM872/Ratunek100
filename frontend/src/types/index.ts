export interface Match {
  id: number
  sport: string
  home_team: string
  away_team: string
  match_date: string
  match_time: string
  home_odds: number | null
  away_odds: number | null
  draw_odds: number | null
  home_win_percentage: number
  away_win_percentage: number
  draw_percentage: number
  qualifies: boolean
  home_wins_in_h2h_last5: number
  away_wins_in_h2h_last5: number
  h2h_count: number
  all_odds?: Record<string, BookmakerOdds>
  form_advantage?: boolean
  home_form_overall?: string[]
  away_form_overall?: string[]
  bookmakers_found?: string[]
  best_home_bookmaker?: string
  best_away_bookmaker?: string
}

export interface BookmakerOdds {
  home: number | null
  away: number | null
  draw: number | null
}

export interface Stats {
  total_matches: number
  qualifying_matches: number
  unique_sports: number
  last_update: string
  sports_breakdown?: Record<string, number>
  bookmakers_coverage?: Record<string, number>
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  count?: number
}

export interface MatchesResponse {
  success: boolean
  matches: Match[]
  count: number
}

export interface StatsResponse {
  success: boolean
  stats: Stats
}

export interface SportsResponse {
  success: boolean
  sports: string[]
}

export interface FilterOptions {
  sport?: string
  qualifies?: 'all' | 'true' | 'false'
  date?: string
  search?: string
  limit?: number
  offset?: number
}
