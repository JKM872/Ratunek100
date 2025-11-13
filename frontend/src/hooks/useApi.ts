import { useQuery, UseQueryResult } from '@tanstack/react-query'
import { matchesApi, statsApi, sportsApi } from '@/lib/api'
import type { Match, Stats, MatchesResponse, FilterOptions } from '@/types'

// Query keys
export const queryKeys = {
  matches: (filters?: FilterOptions) => ['matches', filters] as const,
  match: (id: number) => ['match', id] as const,
  stats: ['stats'] as const,
  sports: ['sports'] as const,
}

// Matches hooks
export function useMatches(filters?: FilterOptions): UseQueryResult<MatchesResponse> {
  return useQuery({
    queryKey: queryKeys.matches(filters),
    queryFn: () => matchesApi.getAll(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchInterval: 1000 * 60 * 10, // Refetch every 10 minutes
  })
}

export function useMatch(id: number): UseQueryResult<Match> {
  return useQuery({
    queryKey: queryKeys.match(id),
    queryFn: () => matchesApi.getById(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  })
}

// Stats hook
export function useStats(): UseQueryResult<Stats> {
  return useQuery({
    queryKey: queryKeys.stats,
    queryFn: statsApi.getStats,
    staleTime: 1000 * 60 * 5,
    refetchInterval: 1000 * 60 * 10,
  })
}

// Sports hook
export function useSports(): UseQueryResult<string[]> {
  return useQuery({
    queryKey: queryKeys.sports,
    queryFn: sportsApi.getAll,
    staleTime: 1000 * 60 * 30, // 30 minutes (sports rarely change)
  })
}
