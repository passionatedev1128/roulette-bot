import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Log API configuration on load (helpful for debugging)
console.log('API Configuration:', {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  API_BASE_URL: API_BASE_URL,
  VITE_WS_URL: import.meta.env.VITE_WS_URL,
  environment: import.meta.env.MODE,
  dev: import.meta.env.DEV,
  prod: import.meta.env.PROD,
});

export const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add request interceptor to log all requests
api.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, config);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Add response interceptor to log all responses
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status, response.data);
    return response;
  },
  (error) => {
    console.error(`[API Response Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.status, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const fetchStatus = async () => {
  const { data } = await api.get('/api/status');
  return data;
};

export const fetchBalance = async () => {
  const { data } = await api.get('/api/balance');
  return data;
};

export const fetchResults = async (limit = 20) => {
  const { data } = await api.get('/api/results/latest', { params: { limit } });
  return data;
};

export const fetchActiveBet = async () => {
  const { data } = await api.get('/api/bets/active');
  return data;
};

export const fetchBetHistory = async (limit = 20) => {
  const { data } = await api.get('/api/bets/history', { params: { limit } });
  return data;
};

export const fetchConfig = async () => {
  try {
    const { data } = await api.get('/api/config/');
    console.log('fetchConfig response:', data);
    // Ensure we return the data in the expected format
    if (data && typeof data === 'object') {
      return data;
    }
    throw new Error('Invalid config response format');
  } catch (error) {
    console.error('fetchConfig error:', error);
    console.error('Response:', error.response?.data);
    throw error;
  }
};

export const updateConfig = async (config, persist = true) => {
  const { data } = await api.put('/api/config/', { config, persist });
  return data;
};

export const savePreset = async (name, config) => {
  const { data } = await api.post('/api/config/preset', { name, config });
  return data;
};

export const fetchPresets = async () => {
  const { data } = await api.get('/api/config/presets');
  return data;
};

export const loadPreset = async (slug) => {
  const { data } = await api.get(`/api/config/preset/${slug}`);
  return data;
};

export const startBot = async ({ mode, testMode }) => {
  const { data } = await api.post('/api/bot/start', { mode, test_mode: testMode });
  return data;
};

export const stopBot = async () => {
  const { data } = await api.post('/api/bot/stop');
  return data;
};

export const changeMode = async (mode) => {
  const { data } = await api.post('/api/bot/mode', { mode });
  return data;
};

export const fetchDailyStats = async () => {
  const { data } = await api.get('/api/stats/daily');
  return data;
};

export const fetchStrategyStats = async () => {
  const { data } = await api.get('/api/stats/strategy');
  return data;
};

export const fetchGaleStats = async () => {
  const { data } = await api.get('/api/stats/gale');
  return data;
};

// Normalize WebSocket URL - convert http(s):// to ws(s):// and handle malformed URLs
const normalizeWebSocketURL = (url) => {
  if (!url) return 'ws://localhost:8000/ws/events';
  
  // Remove any whitespace
  url = url.trim();
  
  // Remove any existing ws:// or wss:// if present (we'll add correct one)
  url = url.replace(/^wss?:\/\//, '');
  
  // If it contains https:// or http://, remove them (keep the domain)
  if (url.includes('https://')) {
    url = url.replace(/https?:\/\//g, '');
  } else if (url.includes('http://')) {
    url = url.replace(/http:\/\//g, '');
  }
  
  // Remove any double slashes (but keep single slashes for paths)
  url = url.replace(/([^:]\/)\/+/g, '$1');
  
  // Determine protocol: use wss:// for HTTPS domains (ngrok, vercel, etc), ws:// for localhost
  if (url.includes('localhost') || url.includes('127.0.0.1')) {
    return 'ws://' + url;
  } else {
    return 'wss://' + url;
  }
};

export const WS_EVENTS_URL = normalizeWebSocketURL(import.meta.env.VITE_WS_URL);


