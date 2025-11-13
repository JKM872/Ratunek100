import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface StatCardProps {
  icon: string
  label: string
  value: string | number
  highlight?: boolean
  className?: string
}

export function StatCard({ icon, label, value, highlight, className }: StatCardProps) {
  return (
    <Card
      className={cn(
        'glass border-l-4 border-blue-500 transition-all hover:shadow-lg',
        highlight && 'ring-2 ring-green-400',
        className
      )}
    >
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600 text-sm font-semibold">{label}</p>
            <p className="text-3xl font-bold text-gray-800 mt-2">{value}</p>
          </div>
          <div className="text-4xl">{icon}</div>
        </div>
      </CardContent>
    </Card>
  )
}
