import { Link, useNavigate } from 'react-router-dom'
import { Target, Bell, Settings, LogOut, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/store/authStore'
import { Badge } from '@/components/ui/badge'

export function Header() {
  const navigate = useNavigate()
  const { user, subscription, logout } = useAuthStore()
  
  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }
  
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

            {/* Subscription badge */}
            {subscription && (
              <Badge className={
                subscription.subscription_type === 'pro' ? 'bg-purple-500/20 text-purple-400' :
                subscription.subscription_type === 'premium' ? 'bg-blue-500/20 text-blue-400' :
                'bg-gray-500/20 text-gray-400'
              }>
                {subscription.subscription_type?.toUpperCase() || 'FREE'}
              </Badge>
            )}

            {/* User menu */}
            <div className="flex items-center gap-2">
              {/* Settings button */}
              <Link to="/settings">
                <Button variant="ghost" size="icon" className="text-gray-700 hover:text-gray-900">
                  <Settings className="w-5 h-5" />
                </Button>
              </Link>
              
              {/* User info */}
              <div className="hidden lg:flex items-center gap-2 px-3 py-2 bg-white/50 rounded-lg">
                <User className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">
                  {user?.email?.split('@')[0]}
                </span>
              </div>
              
              {/* Logout button */}
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="text-gray-700 hover:text-red-600 hover:border-red-300"
              >
                <LogOut className="w-4 h-4 mr-2" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
}
