import { useState, useEffect } from 'react'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Box from '@mui/material/Box'
import Container from '@mui/material/Container'
import Grid from '@mui/material/Grid2'
import Paper from '@mui/material/Paper'
import Typography from '@mui/material/Typography'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import SportsSoccerIcon from '@mui/icons-material/SportsSoccer'
import CircularProgress from '@mui/material/CircularProgress'
import Alert from '@mui/material/Alert'
import Dashboard from './components/Dashboard'
import MatchList from './components/MatchList'
import Statistics from './components/Statistics'
import Filters from './components/Filters'
import axios from 'axios'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#0a1929',
      paper: '#132f4c',
    },
  },
})

export interface Match {
  id: number
  sport: string
  home_team: string
  away_team: string
  match_time: string
  home_odds: number | null
  away_odds: number | null
  home_win_percentage: number | null
  draw_percentage: number | null
  away_win_percentage: number | null
  avg_home_goals: number | null
  avg_away_goals: number | null
  qualifies: number
  created_at: string
}

export interface Stats {
  total_matches: number
  qualifying_matches: number
  avg_odds: number
  last_update: string
}

function App() {
  const [matches, setMatches] = useState<Match[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState({
    sport: 'all',
    qualifies: 'all',
    dateFrom: '',
    dateTo: '',
  })

  const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:7178/api'

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams()
      if (filters.sport !== 'all') params.append('sport', filters.sport)
      if (filters.qualifies !== 'all') params.append('qualifies', filters.qualifies)
      if (filters.dateFrom) params.append('dateFrom', filters.dateFrom)
      if (filters.dateTo) params.append('dateTo', filters.dateTo)

      const [matchesRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE}/matches?${params.toString()}`),
        axios.get(`${API_BASE}/stats`),
      ])

      setMatches(matchesRes.data)
      setStats(statsRes.data)
    } catch (err: any) {
      setError(err.message || 'Błąd podczas pobierania danych')
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 60000) // Odświeżanie co minutę
    return () => clearInterval(interval)
  }, [filters])

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <SportsSoccerIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Livesport Scraper Dashboard
            </Typography>
            <Typography variant="body2" color="inherit" sx={{ opacity: 0.7 }}>
              {stats?.last_update ? `Ostatnia aktualizacja: ${new Date(stats.last_update).toLocaleString('pl-PL')}` : ''}
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flex: 1 }}>
          {loading && (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
              <CircularProgress size={60} />
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {!loading && !error && (
            <Grid container spacing={3}>
              <Grid size={12}>
                <Dashboard stats={stats} />
              </Grid>

              <Grid size={12}>
                <Paper sx={{ p: 2 }}>
                  <Filters filters={filters} setFilters={setFilters} />
                </Paper>
              </Grid>

              <Grid size={12}>
                <MatchList matches={matches} />
              </Grid>

              <Grid size={12}>
                <Statistics matches={matches} />
              </Grid>
            </Grid>
          )}
        </Container>

        <Box
          component="footer"
          sx={{
            py: 3,
            px: 2,
            mt: 'auto',
            backgroundColor: (theme) => theme.palette.background.paper,
            textAlign: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            Livesport Scraper © {new Date().getFullYear()} | Powered by Material-UI & Vite
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  )
}

export default App
