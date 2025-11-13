import { Link } from 'react-router-dom'
import { Target, Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function Header() {
  return (
    <header className="glass sticky top-0 z-50 shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="text-4xl group-hover:scale-110 transition-transform">
              <Target className="w-10 h-10 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                Ratowanie 100
              </h1>
              <p className="text-xs text-gray-600">
                Qualified Betting Matches
              </p>
            </div>
          </Link>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Date/Time */}
            <div className="hidden md:block text-right">
              <p className="text-sm font-semibold text-gray-700">
                🇵🇱 Poland
              </p>
              <p className="text-xs text-gray-600">
                {new Date().toLocaleDateString('pl-PL', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric'
                })}
              </p>
            </div>

            {/* Subscribe Button */}
            <Button className="bg-gradient-to-r from-blue-600 to-blue-700">
              <Bell className="w-4 h-4 mr-2" />
              Subscribe
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
