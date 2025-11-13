import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatCard } from '@/components/StatCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { useStats } from '@/hooks/useApi'
import { AlertCircle, ChartBar, Filter, Bell, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { data: stats, isLoading, error } = useStats()

  if (error) {
    return (
      <div className="glass rounded-lg p-6 text-red-600 border-l-4 border-red-600">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
          <p>Error loading stats: {error.message}</p>
        </div>
      </div>
    )
  }

  if (isLoading || !stats) {
    return <LoadingSpinner text="Loading dashboard..." />
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center text-white mb-12">
        <h1 className="text-5xl font-bold mb-2">🎯 Qualified Matches</h1>
        <p className="text-xl opacity-90">Real-time sports betting insights from Poland</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon="📊"
          label="Total Matches"
          value={stats.total_matches}
          className="border-blue-500"
        />
        <StatCard
          icon="✅"
          label="Qualifying"
          value={stats.qualifying_matches}
          highlight={true}
          className="border-green-500"
        />
        <StatCard
          icon="⚽"
          label="Sports"
          value={stats.unique_sports}
          className="border-orange-500"
        />
        <StatCard
          icon="🕐"
          label="Last Update"
          value={new Date(stats.last_update).toLocaleTimeString('pl-PL', {
            hour: '2-digit',
            minute: '2-digit'
          })}
          className="border-purple-500"
        />
      </div>

      {/* Quick Actions */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="w-6 h-6 mr-2 text-primary" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link to="/matches">
              <Button className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700">
                <ChartBar className="w-4 h-4 mr-2" />
                View All Matches
              </Button>
            </Link>
            <Link to="/matches?qualifies=true">
              <Button className="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700">
                <Filter className="w-4 h-4 mr-2" />
                Qualifying Only
              </Button>
            </Link>
            <Button className="w-full bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700">
              <Bell className="w-4 h-4 mr-2" />
              Subscribe to Email
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* How It Works */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center">
            ℹ️ How It Works
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-gray-700">
          <div className="flex items-start">
            <span className="text-2xl mr-4">1️⃣</span>
            <div>
              <strong className="text-gray-800">Data Collection:</strong> We scrape live match data from LiveSport and bookmaker odds from <span className="bookmaker-fortuna">Fortuna</span>, <span className="bookmaker-superbet">Superbet</span>, and <span className="bookmaker-sts">STS</span>
            </div>
          </div>
          <div className="flex items-start">
            <span className="text-2xl mr-4">2️⃣</span>
            <div>
              <strong className="text-gray-800">Smart Analysis:</strong> Each match is analyzed using H2H statistics, team form, and current odds from multiple bookmakers
            </div>
          </div>
          <div className="flex items-start">
            <span className="text-2xl mr-4">3️⃣</span>
            <div>
              <strong className="text-gray-800">Qualification:</strong> Matches with odds {'>'} 1.37 and strong H2H patterns (60%+ win rate) qualify for our recommendations
            </div>
          </div>
          <div className="flex items-start">
            <span className="text-2xl mr-4">4️⃣</span>
            <div>
              <strong className="text-gray-800">Daily Updates:</strong> Get qualified matches delivered to your email every day at 11:00 AM Polish time
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sports Breakdown */}
      {stats.sports_breakdown && (
        <Card className="glass">
          <CardHeader>
            <CardTitle className="flex items-center">
              📊 Sports Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(stats.sports_breakdown).map(([sport, count]) => (
                <div key={sport} className="text-center p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg">
                  <div className="text-2xl mb-2">
                    {sport === 'Football' && '⚽'}
                    {sport === 'Volleyball' && '🏐'}
                    {sport === 'Handball' && '🤾'}
                    {sport === 'Basketball' && '🏀'}
                    {sport === 'Rugby' && '🏉'}
                    {sport === 'Tennis' && '🎾'}
                  </div>
                  <div className="text-sm font-semibold text-gray-700">{sport}</div>
                  <div className="text-2xl font-bold text-primary mt-2">{count}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
