import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/token', formData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  }
};

export const incidentService = {
  getIncidents: async (params = {}) => {
    const response = await apiClient.get('/incidents', { params });
    return response.data;
  },

  getIncident: async (id) => {
    const response = await apiClient.get(`/incidents/${id}`);
    return response.data;
  },

  createIncident: async (incidentData) => {
    const response = await apiClient.post('/incidents', incidentData);
    return response.data;
  },

  updateIncident: async (id, incidentData) => {
    const response = await apiClient.put(`/incidents/${id}`, incidentData);
    return response.data;
  },

  deleteIncident: async (id) => {
    const response = await apiClient.delete(`/incidents/${id}`);
    return response.data;
  },

  searchIncidents: async (query, params = {}) => {
    const response = await apiClient.get('/incidents/search/full-text', {
      params: { query, ...params }
    });
    return response.data;
  }
};

export const dashboardService = {
  getDashboardData: async () => {
    const response = await apiClient.get('/dashboard/stats');
    return response.data;
  },

  getRecentIncidents: async (limit = 10) => {
    const response = await apiClient.get('/dashboard/recent-incidents', {
      params: { limit }
    });
    return response.data;
  }
};

export const analyticsService = {
  getIncidentTrends: async (days = 30, sectorId = null, severity = null) => {
    const response = await apiClient.get('/analytics/trends', {
      params: { days, sector_id: sectorId, severity }
    });
    return response.data;
  },

  getAPTActivity: async (days = 90) => {
    const response = await apiClient.get('/analytics/apt-activity', {
      params: { days }
    });
    return response.data;
  },

  getSectorAnalysis: async (days = 30) => {
    const response = await apiClient.get('/analytics/sector-analysis', {
      params: { days }
    });
    return response.data;
  },

  getThreatIntelligence: async (days = 7) => {
    const response = await apiClient.get('/analytics/threat-intelligence', {
      params: { days }
    });
    return response.data;
  },

  getGeographicDistribution: async (days = 30) => {
    const response = await apiClient.get('/analytics/geographic-distribution', {
      params: { days }
    });
    return response.data;
  }
};

export const sourceService = {
  getSources: async () => {
    const response = await apiClient.get('/sources');
    return response.data;
  },

  getSource: async (id) => {
    const response = await apiClient.get(`/sources/${id}`);
    return response.data;
  },

  createSource: async (sourceData) => {
    const response = await apiClient.post('/sources', sourceData);
    return response.data;
  },

  updateSource: async (id, sourceData) => {
    const response = await apiClient.put(`/sources/${id}`, sourceData);
    return response.data;
  },

  deleteSource: async (id) => {
    const response = await apiClient.delete(`/sources/${id}`);
    return response.data;
  },

  triggerScraping: async (id) => {
    const response = await apiClient.post(`/sources/${id}/scrape`);
    return response.data;
  }
};

export default apiClient;