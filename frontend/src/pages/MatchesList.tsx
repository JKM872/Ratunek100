import { useState } from 'react'
import { MatchCard } from '@/components/MatchCard'
import { FilterBar } from '@/components/FilterBar'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { useMatches } from '@/hooks/useApi'
import { useFilterStore } from '@/store/filterStore'
import { AlertCircle, ChevronLeft, ChevronRight, Search } from 'lucide-react'

export default function MatchesList() {
  const { filters, setFilters } = useFilterStore()
  const { data, isLoading, error } = useMatches(filters)
  const [page, setPage] = useState(1)

  const handleNextPage = () => {
    const newOffset = (filters.offset || 0) + (filters.limit || 20)
    setFilters({ offset: newOffset })
    setPage(page + 1)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handlePrevPage = () => {
    const newOffset = Math.max(0, (filters.offset || 0) - (filters.limit || 20))
    setFilters({ offset: newOffset })
    setPage(Math.max(1, page - 1))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (error) {
    return (
      <div className="glass rounded-lg p-6 text-red-600 border-l-4 border-red-600">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
          <p>Error loading matches: {error.message}</p>
        </div>
      </div>
    )
  }

  const totalMatches = data?.count || 0
  const matches = data?.matches || []
  const hasNextPage = (filters.offset || 0) + matches.length < totalMatches
  const hasPrevPage = (filters.offset || 0) > 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-white">
        <h1 className="text-4xl font-bold mb-2 flex items-center">
          <Search className="w-8 h-8 mr-3" />
          All Matches
        </h1>
        <p className="text-lg opacity-90">
          Showing {matches.length} of {totalMatches} matches
          {filters.sport && filters.sport !== 'all' && ` • ${filters.sport}`}
          {filters.qualifies === 'true' && ' • Qualifying Only'}
        </p>
      </div>

      {/* Filters */}
      <FilterBar />

      {/* Loading */}
      {isLoading && <LoadingSpinner text="Loading matches..." />}

      {/* Matches Grid */}
      {!isLoading && matches.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {matches.map((match) => (
              <MatchCard
                key={match.id}
                match={match}
                onClick={() => {
                  // TODO: Navigate to match detail page
                  console.log('Match clicked:', match.id)
                }}
              />
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <Button
              onClick={handlePrevPage}
              disabled={!hasPrevPage}
              variant="outline"
              className="glass"
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>
            
            <div className="glass px-6 py-2 rounded-lg font-semibold">
              Page {page}
            </div>
            
            <Button
              onClick={handleNextPage}
              disabled={!hasNextPage}
              variant="outline"
              className="glass"
            >
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </>
      )}

      {/* Empty State */}
      {!isLoading && matches.length === 0 && (
        <div className="glass rounded-lg p-12 text-center">
          <Search className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 text-lg">No matches found for your filters</p>
          <p className="text-gray-500 text-sm mt-2">Try adjusting your search criteria</p>
        </div>
      )}
    </div>
  )
}
