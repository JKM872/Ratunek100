import Grid from '@mui/material/Grid2'
import FormControl from '@mui/material/FormControl'
import InputLabel from '@mui/material/InputLabel'
import Select from '@mui/material/Select'
import MenuItem from '@mui/material/MenuItem'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'

interface FiltersProps {
  filters: {
    sport: string
    qualifies: string
    dateFrom: string
    dateTo: string
  }
  setFilters: (filters: any) => void
}

export default function Filters({ filters, setFilters }: FiltersProps) {
  const handleChange = (field: string, value: string) => {
    setFilters({ ...filters, [field]: value })
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Filtry
      </Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <FormControl fullWidth size="small">
            <InputLabel>Sport</InputLabel>
            <Select
              value={filters.sport}
              label="Sport"
              onChange={(e) => handleChange('sport', e.target.value)}
            >
              <MenuItem value="all">Wszystkie</MenuItem>
              <MenuItem value="football">Piłka nożna</MenuItem>
              <MenuItem value="tennis">Tenis</MenuItem>
              <MenuItem value="basketball">Koszykówka</MenuItem>
              <MenuItem value="volleyball">Siatkówka</MenuItem>
              <MenuItem value="hockey">Hockey</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <FormControl fullWidth size="small">
            <InputLabel>Kwalifikacja</InputLabel>
            <Select
              value={filters.qualifies}
              label="Kwalifikacja"
              onChange={(e) => handleChange('qualifies', e.target.value)}
            >
              <MenuItem value="all">Wszystkie</MenuItem>
              <MenuItem value="1">Tylko kwalifikujące</MenuItem>
              <MenuItem value="0">Niekwalifikujące</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            size="small"
            label="Data od"
            type="date"
            value={filters.dateFrom}
            onChange={(e) => handleChange('dateFrom', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <TextField
            fullWidth
            size="small"
            label="Data do"
            type="date"
            value={filters.dateTo}
            onChange={(e) => handleChange('dateTo', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
      </Grid>
    </Box>
  )
}
