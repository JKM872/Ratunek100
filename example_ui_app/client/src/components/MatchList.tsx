import Paper from '@mui/material/Paper'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Typography from '@mui/material/Typography'
import Chip from '@mui/material/Chip'
import Box from '@mui/material/Box'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import type { Match } from '../App'

interface MatchListProps {
  matches: Match[]
}

export default function MatchList({ matches }: MatchListProps) {
  const getSportColor = (sport: string) => {
    const colors: Record<string, string> = {
      football: '#4caf50',
      tennis: '#ff9800',
      basketball: '#2196f3',
      volleyball: '#9c27b0',
      hockey: '#00bcd4',
    }
    return colors[sport.toLowerCase()] || '#757575'
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom component="div" sx={{ mb: 2 }}>
        Lista meczów ({matches.length})
      </Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Sport</TableCell>
              <TableCell>Gospodarze</TableCell>
              <TableCell>Goście</TableCell>
              <TableCell align="center">Data i godzina</TableCell>
              <TableCell align="center">Kurs goście</TableCell>
              <TableCell align="center">H2H Goście %</TableCell>
              <TableCell align="center">Śr. Bramki Goście</TableCell>
              <TableCell align="center">Kwalifikuje</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {matches.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                    Brak meczów do wyświetlenia
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              matches.map((match) => (
                <TableRow key={match.id} hover>
                  <TableCell>
                    <Chip
                      label={match.sport}
                      size="small"
                      sx={{
                        bgcolor: getSportColor(match.sport),
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {match.home_team}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {match.away_team}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2">
                      {new Date(match.match_time).toLocaleString('pl-PL')}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2" fontWeight="bold" color="primary">
                      {match.away_odds?.toFixed(2) || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Box
                      sx={{
                        display: 'inline-block',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        bgcolor: match.away_win_percentage && match.away_win_percentage >= 60 ? '#4caf5022' : 'transparent',
                      }}
                    >
                      <Typography variant="body2" fontWeight="bold">
                        {match.away_win_percentage?.toFixed(1) || '-'}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2">
                      {match.avg_away_goals?.toFixed(2) || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    {match.qualifies ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <CancelIcon color="error" />
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  )
}
