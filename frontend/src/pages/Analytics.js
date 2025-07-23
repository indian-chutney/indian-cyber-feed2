import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import { useQuery } from 'react-query';
import { analyticsService } from '../services/authService';
import ThreatTrendsChart from '../components/ThreatTrendsChart';
import SectorBreakdownChart from '../components/SectorBreakdownChart';

const Analytics = () => {
  const [trendDays, setTrendDays] = useState(30);
  const [sectorDays, setSectorDays] = useState(30);

  const { data: trends } = useQuery(
    ['incidentTrends', trendDays],
    () => analyticsService.getIncidentTrends(trendDays)
  );

  const { data: sectorAnalysis } = useQuery(
    ['sectorAnalysis', sectorDays],
    () => analyticsService.getSectorAnalysis(sectorDays)
  );

  const { data: aptActivity } = useQuery(
    'aptActivity',
    () => analyticsService.getAPTActivity(90)
  );

  const { data: threatIntel } = useQuery(
    'threatIntelligence',
    () => analyticsService.getThreatIntelligence(7)
  );

  const { data: geoDistribution } = useQuery(
    'geoDistribution',
    () => analyticsService.getGeographicDistribution(30)
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Threat Analytics
        </Typography>

        {/* Incident Trends */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Incident Trends
                </Typography>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Period</InputLabel>
                  <Select
                    value={trendDays}
                    label="Period"
                    onChange={(e) => setTrendDays(e.target.value)}
                  >
                    <MenuItem value={7}>7 Days</MenuItem>
                    <MenuItem value={30}>30 Days</MenuItem>
                    <MenuItem value={90}>90 Days</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              {trends?.trends && (
                <ThreatTrendsChart 
                  data={trends.trends.map(item => ({
                    date: item.date,
                    incident_count: item.count
                  }))} 
                />
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Sector Analysis and APT Activity */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Sector Analysis
                </Typography>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Period</InputLabel>
                  <Select
                    value={sectorDays}
                    label="Period"
                    onChange={(e) => setSectorDays(e.target.value)}
                  >
                    <MenuItem value={7}>7 Days</MenuItem>
                    <MenuItem value={30}>30 Days</MenuItem>
                    <MenuItem value={90}>90 Days</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              {sectorAnalysis?.sectors && (
                <SectorBreakdownChart 
                  data={sectorAnalysis.sectors.map(sector => ({
                    sector_name: sector.name,
                    incident_count: sector.incident_count,
                    critical_count: sector.critical_count
                  }))} 
                />
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Top APT Groups
              </Typography>
              <List>
                {aptActivity?.apt_groups?.slice(0, 5).map((apt, index) => (
                  <ListItem key={index} divider>
                    <ListItemText
                      primary={apt.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {apt.origin_country}
                          </Typography>
                          <Chip 
                            label={`${apt.incident_count} incidents`}
                            size="small"
                            color="warning"
                            sx={{ mt: 1 }}
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>

        {/* Threat Intelligence and Geographic Distribution */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  High-Severity Incidents (7 days)
                </Typography>
                <List>
                  {threatIntel?.high_severity_incidents?.slice(0, 3).map((incident, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={incident.title}
                        secondary={
                          <Box>
                            <Chip 
                              label={incident.severity}
                              size="small"
                              color="error"
                              sx={{ mr: 1 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              Score: {(incident.relevance_score * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Geographic Distribution
                </Typography>
                <List>
                  {geoDistribution?.geographic_data?.slice(0, 5).map((geo, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={geo.location}
                        secondary={`${geo.incident_count} incidents`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Analytics;