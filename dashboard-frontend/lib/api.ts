/**
 * API Client for Kingdom-77 Dashboard
 */

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const auth = {
  getLoginUrl: () => api.get('/api/auth/login-url'),
  login: (code: string) => api.post('/api/auth/login', { code }),
  logout: () => api.post('/api/auth/logout'),
  me: () => api.get('/api/auth/me'),
};

// Servers endpoints
export const servers = {
  list: () => api.get('/api/servers'),
  get: (guildId: string) => api.get(`/api/servers/${guildId}`),
  getSettings: (guildId: string) => api.get(`/api/servers/${guildId}/settings`),
  updateSettings: (guildId: string, settings: any) =>
    api.put(`/api/servers/${guildId}/settings`, settings),
};

// Stats endpoints
export const stats = {
  overview: (guildId: string) => api.get(`/api/stats/${guildId}/overview`),
  leveling: (guildId: string) => api.get(`/api/stats/${guildId}/leveling`),
  moderation: (guildId: string) => api.get(`/api/stats/${guildId}/moderation`),
  tickets: (guildId: string) => api.get(`/api/stats/${guildId}/tickets`),
};

// Moderation endpoints
export const moderation = {
  logs: (guildId: string, limit = 50, offset = 0) =>
    api.get(`/api/moderation/${guildId}/logs`, { params: { limit, offset } }),
  warnings: (guildId: string, userId: string) =>
    api.get(`/api/moderation/${guildId}/warnings/${userId}`),
  deleteWarning: (guildId: string, warningId: string) =>
    api.delete(`/api/moderation/${guildId}/warnings/${warningId}`),
};

// Leveling endpoints
export const leveling = {
  leaderboard: (guildId: string, limit = 100) =>
    api.get(`/api/leveling/${guildId}/leaderboard`, { params: { limit } }),
  user: (guildId: string, userId: string) =>
    api.get(`/api/leveling/${guildId}/user/${userId}`),
  rewards: (guildId: string) => api.get(`/api/leveling/${guildId}/rewards`),
  addReward: (guildId: string, level: number, roleId: string) =>
    api.post(`/api/leveling/${guildId}/rewards`, { level, role_id: roleId }),
  deleteReward: (guildId: string, level: number) =>
    api.delete(`/api/leveling/${guildId}/rewards/${level}`),
};

// Tickets endpoints
export const tickets = {
  list: (guildId: string, status?: string, limit = 50) =>
    api.get(`/api/tickets/${guildId}/tickets`, { params: { status, limit } }),
  get: (guildId: string, ticketId: string) =>
    api.get(`/api/tickets/${guildId}/tickets/${ticketId}`),
};

// Settings endpoints
export const settings = {
  get: (guildId: string) => api.get(`/api/settings/${guildId}`),
  update: (guildId: string, settings: any) =>
    api.put(`/api/settings/${guildId}`, settings),
  reset: (guildId: string) => api.post(`/api/settings/${guildId}/reset`),
};

export default api;
