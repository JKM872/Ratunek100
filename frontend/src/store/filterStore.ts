import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { FilterOptions } from '@/types'

interface FilterState {
  filters: FilterOptions
  setFilters: (filters: Partial<FilterOptions>) => void
  resetFilters: () => void
}

const defaultFilters: FilterOptions = {
  sport: 'all',
  qualifies: 'true',
  date: '',
  search: '',
  limit: 20,
  offset: 0,
}

export const useFilterStore = create<FilterState>()(
  persist(
    (set) => ({
      filters: defaultFilters,
      setFilters: (newFilters) =>
        set((state) => ({
          filters: { ...state.filters, ...newFilters },
        })),
      resetFilters: () => set({ filters: defaultFilters }),
    }),
    {
      name: 'filter-storage',
    }
  )
)
