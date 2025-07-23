import React from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Place as PlaceIcon
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { dashboardService, analyticsService } from '../services/authService';
import ThreatTrendsChart from '../components/ThreatTrendsChart';
import SectorBreakdownChart from '../components/SectorBreakdownChart';

const Dashboard = () => {
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery(
    'dashboardData',
    dashboardService.getDashboardData
  );

  const { data: threatIntel, isLoading: threatIntelLoading } = useQuery(
    'threatIntelligence',
    () => analyticsService.getThreatIntelligence(7)
  );

  if (dashboardLoading || threatIntelLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ width: '100%', mt: 4 }}>
          <LinearProgress />
        </Box>
      </Container>
    );
  }

  const stats = dashboardData?.stats || {};
  const recentIncidents = dashboardData?.recent_incidents || [];
  const sectorStats = dashboardData?.sector_stats || [];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Cyber Threat Intelligence Dashboard
        </Typography>
        
        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <SecurityIcon color="primary" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Incidents
                    </Typography>
                    <Typography variant="h5">
                      {stats.total_incidents || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <WarningIcon color="error" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Critical Incidents
                    </Typography>
                    <Typography variant="h5">
                      {stats.critical_incidents || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUpIcon color="warning" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Open Incidents
                    </Typography>
                    <Typography variant="h5">
                      {stats.open_incidents || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PlaceIcon color="info" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Resolved
                    </Typography>
                    <Typography variant="h5">
                      {stats.resolved_incidents || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Charts and Recent Incidents */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Threat Trends (Last 30 Days)
              </Typography>
              <ThreatTrendsChart data={dashboardData?.threat_trends || []} />
            </Paper>
            
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Sector Breakdown
              </Typography>
              <SectorBreakdownChart data={sectorStats} />
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recent Incidents
              </Typography>
              <List>
                {recentIncidents.slice(0, 5).map((incident, index) => (
                  <ListItem key={incident.id || index} divider>
                    <ListItemText
                      primary={incident.title}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(incident.discovered_date).toLocaleDateString()}
                          </Typography>
                          <Chip 
                            label={incident.severity} 
                            size="small" 
                            color={getSeverityColor(incident.severity)}
                            sx={{ mt: 1 }}
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
            
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Threat Intelligence Summary
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  High-Severity Incidents (7 days)
                </Typography>
                <Typography variant="h6">
                  {threatIntel?.high_severity_incidents?.length || 0}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Emerging Threats
                </Typography>
                <Typography variant="h6">
                  {threatIntel?.emerging_threats?.length || 0}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Total IOCs
                </Typography>
                <Typography variant="h6">
                  {threatIntel?.total_iocs || 0}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard;