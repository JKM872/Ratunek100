import React from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { AlertCircle, Loader2, TrendingUp } from 'lucide-react';

interface BookmakerOddsProps {
  matchKey: string;
  date?: string;
}

interface BookmakerData {
  bookmaker: string;
  home_odds: number | null;
  draw_odds: number | null;
  away_odds: number | null;
  created_at: string;
  updated_at: string;
}

interface BookmakerOddsResponse {
  success: boolean;
  match_key?: string;
  bookmakers?: Record<string, BookmakerData>;
  last_update?: string;
  message?: string;
}

const BOOKMAKER_COLORS = {
  Fortuna: {
    bg: 'bg-red-50',
    border: 'border-l-red-500',
    text: 'text-red-900',
    badge: 'bg-red-100 text-red-800',
    priority: true
  },
  Superbet: {
    bg: 'bg-blue-50',
    border: 'border-l-blue-500',
    text: 'text-blue-900',
    badge: 'bg-blue-100 text-blue-800',
    priority: false
  },
  STS: {
    bg: 'bg-green-50',
    border: 'border-l-green-500',
    text: 'text-green-900',
    badge: 'bg-green-100 text-green-800',
    priority: false
  }
};

async function fetchBookmakerOdds(matchKey: string, date?: string): Promise<BookmakerOddsResponse> {
  const params = new URLSearchParams({ match_key: matchKey });
  if (date) params.append('date', date);
  
  const response = await axios.get(`/api/bookmaker-odds?${params.toString()}`);
  return response.data;
}

export function BookmakerOdds({ matchKey, date }: BookmakerOddsProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['bookmaker-odds', matchKey, date],
    queryFn: () => fetchBookmakerOdds(matchKey, date),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-4">
        <Loader2 className="w-5 h-5 animate-spin text-primary mr-2" />
        <span className="text-sm text-muted-foreground">Ładowanie kursów polskich bukmacherów...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-4 text-amber-600">
        <AlertCircle className="w-5 h-5 mr-2" />
        <span className="text-sm">Nie udało się pobrać kursów bukmacherów</span>
      </div>
    );
  }

  if (!data?.success || !data.bookmakers || Object.keys(data.bookmakers).length === 0) {
    return (
      <div className="flex items-center justify-center py-4 text-muted-foreground">
        <AlertCircle className="w-5 h-5 mr-2" />
        <span className="text-sm">{data?.message || 'Brak kursów od polskich bukmacherów'}</span>
      </div>
    );
  }

  const bookmakers = Object.values(data.bookmakers);
  
  // Sort: Fortuna first (priority), then alphabetically
  bookmakers.sort((a, b) => {
    const aConfig = BOOKMAKER_COLORS[a.bookmaker as keyof typeof BOOKMAKER_COLORS];
    const bConfig = BOOKMAKER_COLORS[b.bookmaker as keyof typeof BOOKMAKER_COLORS];
    
    if (aConfig?.priority && !bConfig?.priority) return -1;
    if (!aConfig?.priority && bConfig?.priority) return 1;
    return a.bookmaker.localeCompare(b.bookmaker);
  });

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground flex items-center">
          <TrendingUp className="w-4 h-4 mr-2 text-primary" />
          Kursy Polskich Bukmacherów 🇵🇱
        </h3>
        {data.last_update && (
          <span className="text-xs text-muted-foreground">
            {new Date(data.last_update).toLocaleString('pl-PL')}
          </span>
        )}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {bookmakers.map((bookmaker) => {
          const config = BOOKMAKER_COLORS[bookmaker.bookmaker as keyof typeof BOOKMAKER_COLORS] || {
            bg: 'bg-gray-50',
            border: 'border-l-gray-500',
            text: 'text-gray-900',
            badge: 'bg-gray-100 text-gray-800',
            priority: false
          };

          return (
            <Card
              key={bookmaker.bookmaker}
              className={`${config.bg} ${config.border} border-l-4 transition-all hover:shadow-md`}
            >
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center justify-between text-sm">
                  <span className={config.text}>{bookmaker.bookmaker}</span>
                  {config.priority && (
                    <Badge variant="secondary" className={config.badge}>
                      PRIORITY
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-2 text-center">
                  {/* Home Odds */}
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Gosp</div>
                    <div className={`text-lg font-bold ${config.text}`}>
                      {bookmaker.home_odds ? bookmaker.home_odds.toFixed(2) : '-'}
                    </div>
                  </div>

                  {/* Draw Odds (if available) */}
                  {bookmaker.draw_odds !== null && (
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Remis</div>
                      <div className={`text-lg font-bold ${config.text}`}>
                        {bookmaker.draw_odds ? bookmaker.draw_odds.toFixed(2) : '-'}
                      </div>
                    </div>
                  )}

                  {/* Away Odds */}
                  <div className={bookmaker.draw_odds === null ? 'col-span-1' : ''}>
                    <div className="text-xs text-muted-foreground mb-1">Gość</div>
                    <div className={`text-lg font-bold ${config.text}`}>
                      {bookmaker.away_odds ? bookmaker.away_odds.toFixed(2) : '-'}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="text-xs text-center text-muted-foreground pt-2 border-t">
        Kursy pobrane ze strony bukmachera • Sprawdź warunki zakładu przed postawieniem
      </div>
    </div>
  );
}
