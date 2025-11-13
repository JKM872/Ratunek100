import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Calendar, Clock, TrendingUp, ExternalLink } from 'lucide-react'
import { cn, getSportIcon, getSportBadgeClass, formatMatchOdds } from '@/lib/utils'
import type { Match } from '@/types'

interface MatchCardProps {
  match: Match
  onClick?: () => void
}

export function MatchCard({ match, onClick }: MatchCardProps) {
  return (
    <Card className="match-card glass border-l-4 border-blue-500 hover:shadow-xl transition-all">
      <CardContent className="p-6">
        {/* Header with Sport and Qualify Badge */}
        <div className="flex justify-between items-start mb-4">
          <Badge className={cn('sport-badge', getSportBadgeClass(match.sport))}>
            {getSportIcon(match.sport)} {match.sport}
          </Badge>
          {match.qualifies && (
            <Badge className="bg-green-100 text-green-800 hover:bg-green-200">
              ✅ QUALIFIES
            </Badge>
          )}
        </div>

        {/* Teams */}
        <div className="mb-4 text-center">
          <div className="text-lg font-bold text-gray-800">{match.home_team}</div>
          <div className="text-gray-500 text-sm my-2">vs</div>
          <div className="text-lg font-bold text-gray-800">{match.away_team}</div>
        </div>

        {/* Date/Time */}
        <div className="flex items-center justify-center space-x-4 mb-4 text-sm text-gray-600">
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-1" />
            {match.match_date}
          </div>
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            {match.match_time || 'TBA'}
          </div>
        </div>

        {/* Odds */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-4">
          <div className="text-center">
            <div className="text-xs text-gray-500 mb-2">
              BEST ODDS {match.bookmakers_found?.length ? `(${match.bookmakers_found.join(', ')})` : ''}
            </div>
            <div className="text-xl font-bold text-gray-800">
              {formatMatchOdds(match)}
            </div>
            {match.best_home_bookmaker && match.best_away_bookmaker && (
              <div className="text-xs text-gray-500 mt-2">
                H: {match.best_home_bookmaker} | A: {match.best_away_bookmaker}
              </div>
            )}
          </div>
        </div>

        {/* Win Percentages */}
        <div className="grid grid-cols-3 gap-2 text-center text-sm mb-4">
          <div>
            <div className="text-gray-600 text-xs">Home Win</div>
            <div className="text-lg font-bold text-blue-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              {match.home_win_percentage?.toFixed(0)}%
            </div>
          </div>
          <div>
            <div className="text-gray-600 text-xs">Draw</div>
            <div className="text-lg font-bold text-gray-600">
              {match.draw_percentage?.toFixed(0)}%
            </div>
          </div>
          <div>
            <div className="text-gray-600 text-xs">Away Win</div>
            <div className="text-lg font-bold text-orange-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              {match.away_win_percentage?.toFixed(0)}%
            </div>
          </div>
        </div>

        {/* H2H Stats */}
        {match.h2h_count > 0 && (
          <div className="text-center text-sm text-gray-600 mb-4">
            H2H Last 5: <span className="font-bold">{match.home_wins_in_h2h_last5}-{match.away_wins_in_h2h_last5}</span>
            <span className="text-xs ml-1">(from {match.h2h_count} matches)</span>
          </div>
        )}

        {/* Form Advantage Badge */}
        {match.form_advantage && (
          <div className="flex justify-center mb-2">
            <Badge className="bg-orange-100 text-orange-800">
              🔥 Form Advantage
            </Badge>
          </div>
        )}
      </CardContent>

      <CardFooter className="p-6 pt-0">
        <Button
          onClick={onClick}
          className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
        >
          <ExternalLink className="w-4 h-4 mr-2" />
          View Details
        </Button>
      </CardFooter>
    </Card>
  )
}
