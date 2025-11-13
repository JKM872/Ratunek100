import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

export function formatTime(time: string): string {
  return time || 'TBA'
}

export function formatOdds(odds: number | null | undefined): string {
  if (!odds) return '-'
  return odds.toFixed(2)
}

export function getSportIcon(sport: string): string {
  const icons: Record<string, string> = {
    'Football': '⚽',
    'Volleyball': '🏐',
    'Handball': '🤾',
    'Basketball': '🏀',
    'Rugby': '🏉',
    'Tennis': '🎾',
  }
  return icons[sport] || '🎯'
}

export function getSportBadgeClass(sport: string): string {
  const classes: Record<string, string> = {
    'Football': 'sport-football',
    'Volleyball': 'sport-volleyball',
    'Handball': 'sport-handball',
    'Basketball': 'sport-basketball',
    'Rugby': 'sport-rugby',
    'Tennis': 'sport-tennis',
  }
  return classes[sport] || 'sport-football'
}

export function formatMatchOdds(match: any): string {
  const { sport, home_odds, draw_odds, away_odds } = match
  
  // Sports without draw
  const noDrawSports = ['Volleyball', 'Handball', 'Rugby', 'Tennis']
  
  if (noDrawSports.includes(sport)) {
    if (home_odds && away_odds) {
      return `${formatOdds(home_odds)} / ${formatOdds(away_odds)}`
    }
  } else {
    // Traditional sports with draw
    if (home_odds && draw_odds && away_odds) {
      return `${formatOdds(home_odds)} / ${formatOdds(draw_odds)} / ${formatOdds(away_odds)}`
    }
  }
  
  return 'N/A'
}

/**
 * Generate normalized match key for bookmaker odds lookup
 * Matches the format used by local_bookmaker_scraper.py
 */
export function generateMatchKey(homeTeam: string, awayTeam: string, matchDate: string): string {
  const normalizeTeamName = (team: string): string => {
    if (!team) return ''
    
    // Remove common suffixes
    let normalized = team.replace(/\s+(FC|CF|AC|SC|BK|SK|GKS|KS|MKS|TS|VfL|VfB|BSC|FSV)\s*$/gi, '')
    
    // Remove accents and special chars, lowercase
    normalized = normalized.trim().toLowerCase()
    normalized = normalized.replace(/[^\w\s-]/g, '')
    normalized = normalized.replace(/\s+/g, ' ')
    
    return normalized
  }
  
  const home = normalizeTeamName(homeTeam)
  const away = normalizeTeamName(awayTeam)
  
  return `${home}_vs_${away}_${matchDate}`
}
