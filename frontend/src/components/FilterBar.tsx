import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Filter, RotateCcw } from 'lucide-react'
import { useFilterStore } from '@/store/filterStore'
import { useSports } from '@/hooks/useApi'

export function FilterBar() {
  const { filters, setFilters, resetFilters } = useFilterStore()
  const { data: sports } = useSports()

  const handleChange = (key: string, value: string) => {
    setFilters({ [key]: value, offset: 0 }) // Reset offset on filter change
  }

  return (
    <Card className="glass">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-800 flex items-center">
            <Filter className="w-5 h-5 mr-2" />
            Filters
          </h2>
          <Button
            variant="outline"
            size="sm"
            onClick={resetFilters}
            className="text-gray-600"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Sport Filter */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Sport
            </label>
            <select
              value={filters.sport || 'all'}
              onChange={(e) => handleChange('sport', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-white"
            >
              <option value="all">All Sports</option>
              {sports?.map((sport) => (
                <option key={sport} value={sport}>
                  {sport}
                </option>
              ))}
            </select>
          </div>

          {/* Qualifying Filter */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.qualifies || 'all'}
              onChange={(e) => handleChange('qualifies', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-white"
            >
              <option value="all">All Matches</option>
              <option value="true">Qualifying Only</option>
              <option value="false">Non-Qualifying</option>
            </select>
          </div>

          {/* Date Filter */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Date
            </label>
            <input
              type="date"
              value={filters.date || ''}
              onChange={(e) => handleChange('date', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-white"
            />
          </div>

          {/* Limit Filter */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Per Page
            </label>
            <select
              value={filters.limit || 20}
              onChange={(e) => handleChange('limit', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-white"
            >
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
