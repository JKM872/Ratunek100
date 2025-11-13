import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, List } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  {
    name: 'Dashboard',
    path: '/',
    icon: LayoutDashboard,
  },
  {
    name: 'Matches',
    path: '/matches',
    icon: List,
  },
]

export function Navigation() {
  const location = useLocation()

  return (
    <nav className="glass sticky top-[89px] z-40 shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex space-x-8">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  'flex items-center px-4 py-3 font-semibold transition-all border-b-2',
                  isActive
                    ? 'text-primary border-primary'
                    : 'text-gray-600 border-transparent hover:text-gray-800 hover:border-gray-300'
                )}
              >
                <Icon className="w-4 h-4 mr-2" />
                {item.name}
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
