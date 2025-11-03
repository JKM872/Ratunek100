import Paper from '@mui/material/Paper'
import Typography from '@mui/material/Typography'
import Grid from '@mui/material/Grid2'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import type { Match } from '../App'

interface StatisticsProps {
  matches: Match[]
}

export default function Statistics({ matches }: StatisticsProps) {
  // Statystyki sportów
  const sportStats = matches.reduce((acc: any, match) => {
    const sport = match.sport
    if (!acc[sport]) {
      acc[sport] = { sport, total: 0, qualifying: 0 }
    }
    acc[sport].total++
    if (match.qualifies) acc[sport].qualifying++
    return acc
  }, {})

  const sportData = Object.values(sportStats)

  // Statystyki kwalifikacji
  const qualifyingStats = [
    {
      name: 'Kwalifikujące',
      value: matches.filter(m => m.qualifies).length,
      color: '#4caf50',
    },
    {
      name: 'Niekwalifikujące',
      value: matches.filter(m => !m.qualifies).length,
      color: '#f44336',
    },
  ]

  // Rozkład kursów
  const oddsRanges = [
    { range: '1.0-2.0', count: 0 },
    { range: '2.0-3.0', count: 0 },
    { range: '3.0-4.0', count: 0 },
    { range: '4.0-5.0', count: 0 },
    { range: '5.0+', count: 0 },
  ]

  matches.forEach(match => {
    if (!match.away_odds) return
    const odds = match.away_odds
    if (odds >= 1 && odds < 2) oddsRanges[0].count++
    else if (odds >= 2 && odds < 3) oddsRanges[1].count++
    else if (odds >= 3 && odds < 4) oddsRanges[2].count++
    else if (odds >= 4 && odds < 5) oddsRanges[3].count++
    else if (odds >= 5) oddsRanges[4].count++
  })

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Mecze według sportów
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sportData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="sport" stroke="#999" />
              <YAxis stroke="#999" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#132f4c',
                  border: '1px solid #444',
                  borderRadius: '4px',
                }}
              />
              <Legend />
              <Bar dataKey="total" name="Wszystkie" fill="#2196f3" />
              <Bar dataKey="qualifying" name="Kwalifikujące" fill="#4caf50" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Kwalifikacja meczów
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={qualifyingStats}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {qualifyingStats.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#132f4c',
                  border: '1px solid #444',
                  borderRadius: '4px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      <Grid size={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Rozkład kursów na gości
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={oddsRanges}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="range" stroke="#999" />
              <YAxis stroke="#999" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#132f4c',
                  border: '1px solid #444',
                  borderRadius: '4px',
                }}
              />
              <Legend />
              <Bar dataKey="count" name="Liczba meczów" fill="#ff9800" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>
    </Grid>
  )
}
