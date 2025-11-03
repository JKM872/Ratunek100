import Grid from '@mui/material/Grid2'
import Paper from '@mui/material/Paper'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import SportsIcon from '@mui/icons-material/Sports'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import UpdateIcon from '@mui/icons-material/Update'
import type { Stats } from '../App'

interface DashboardProps {
  stats: Stats | null
}

export default function Dashboard({ stats }: DashboardProps) {
  if (!stats) return null

  const cards = [
    {
      title: 'Mecze kwalifikujące się',
      value: stats.qualifying_matches,
      icon: <CheckCircleIcon fontSize="large" />,
      color: '#4caf50',
    },
    {
      title: 'Wszystkie mecze',
      value: stats.total_matches,
      icon: <SportsIcon fontSize="large" />,
      color: '#2196f3',
    },
    {
      title: 'Średnie kursy',
      value: stats.avg_odds.toFixed(2),
      icon: <TrendingUpIcon fontSize="large" />,
      color: '#ff9800',
    },
    {
      title: 'Ostatnia aktualizacja',
      value: new Date(stats.last_update).toLocaleTimeString('pl-PL'),
      icon: <UpdateIcon fontSize="large" />,
      color: '#9c27b0',
    },
  ]

  return (
    <Grid container spacing={3}>
      {cards.map((card, index) => (
        <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
          <Paper
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
              background: `linear-gradient(135deg, ${card.color}22 0%, ${card.color}11 100%)`,
              border: `1px solid ${card.color}44`,
            }}
          >
            <Box display="flex" justifyContent="space-between" alignItems="flex-start">
              <Box>
                <Typography variant="h4" component="div" fontWeight="bold" color={card.color}>
                  {card.value}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {card.title}
                </Typography>
              </Box>
              <Box sx={{ color: card.color, opacity: 0.6 }}>
                {card.icon}
              </Box>
            </Box>
          </Paper>
        </Grid>
      ))}
    </Grid>
  )
}
