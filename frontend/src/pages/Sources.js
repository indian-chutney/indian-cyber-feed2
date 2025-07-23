import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { sourceService } from '../services/authService';

const Sources = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingSource, setEditingSource] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    source_type: '',
    scraping_interval: 3600,
    is_active: true
  });

  const queryClient = useQueryClient();

  const { data: sources, isLoading } = useQuery('sources', sourceService.getSources);

  const createMutation = useMutation(sourceService.createSource, {
    onSuccess: () => {
      queryClient.invalidateQueries('sources');
      handleCloseDialog();
    }
  });

  const updateMutation = useMutation(
    ({ id, data }) => sourceService.updateSource(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('sources');
        handleCloseDialog();
      }
    }
  );

  const deleteMutation = useMutation(sourceService.deleteSource, {
    onSuccess: () => {
      queryClient.invalidateQueries('sources');
    }
  });

  const scrapeMutation = useMutation(sourceService.triggerScraping);

  const handleOpenDialog = (source = null) => {
    if (source) {
      setEditingSource(source);
      setFormData({
        name: source.name,
        url: source.url,
        source_type: source.source_type,
        scraping_interval: source.scraping_interval,
        is_active: source.is_active
      });
    } else {
      setEditingSource(null);
      setFormData({
        name: '',
        url: '',
        source_type: '',
        scraping_interval: 3600,
        is_active: true
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingSource(null);
  };

  const handleSubmit = () => {
    if (editingSource) {
      updateMutation.mutate({ id: editingSource.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (sourceId) => {
    if (window.confirm('Are you sure you want to delete this source?')) {
      deleteMutation.mutate(sourceId);
    }
  };

  const handleScrape = (sourceId) => {
    scrapeMutation.mutate(sourceId);
  };

  const getSourceTypeLabel = (type) => {
    const labels = {
      forum: 'Forum',
      paste_site: 'Paste Site',
      social_media: 'Social Media',
      blog: 'Blog',
      github: 'GitHub',
      security_feed: 'Security Feed',
      news: 'News'
    };
    return labels[type] || type;
  };

  const getSourceTypeColor = (type) => {
    const colors = {
      security_feed: 'primary',
      github: 'secondary',
      blog: 'info',
      paste_site: 'warning',
      forum: 'success',
      social_media: 'error',
      news: 'default'
    };
    return colors[type] || 'default';
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Data Sources
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Source
          </Button>
        </Box>

        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>URL</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Interval (hrs)</TableCell>
                  <TableCell>Last Scraped</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sources?.map((source) => (
                  <TableRow key={source.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        {source.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {source.url}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getSourceTypeLabel(source.source_type)}
                        color={getSourceTypeColor(source.source_type)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={source.is_active ? 'Active' : 'Inactive'}
                        color={source.is_active ? 'success' : 'default'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {(source.scraping_interval / 3600).toFixed(1)}
                    </TableCell>
                    <TableCell>
                      {source.last_scraped 
                        ? new Date(source.last_scraped).toLocaleString()
                        : 'Never'
                      }
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleScrape(source.id)}
                        title="Trigger Scraping"
                      >
                        <PlayIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleOpenDialog(source)}
                        title="Edit"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(source.id)}
                        title="Delete"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Add/Edit Dialog */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            {editingSource ? 'Edit Source' : 'Add New Source'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="URL"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Source Type</InputLabel>
                  <Select
                    value={formData.source_type}
                    label="Source Type"
                    onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
                  >
                    <MenuItem value="security_feed">Security Feed</MenuItem>
                    <MenuItem value="github">GitHub</MenuItem>
                    <MenuItem value="blog">Blog</MenuItem>
                    <MenuItem value="paste_site">Paste Site</MenuItem>
                    <MenuItem value="forum">Forum</MenuItem>
                    <MenuItem value="social_media">Social Media</MenuItem>
                    <MenuItem value="news">News</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Scraping Interval (seconds)"
                  type="number"
                  value={formData.scraping_interval}
                  onChange={(e) => setFormData({ ...formData, scraping_interval: parseInt(e.target.value) })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained">
              {editingSource ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default Sources;