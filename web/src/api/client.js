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
  headers: {
    // Skip ngrok browser warning page for ngrok free tier
    'ngrok-skip-browser-warning': 'true',
  },
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
    console.log('[fetchConfig] Starting request to:', api.defaults.baseURL + '/api/config/');
    const response = await api.get('/api/config/');
    const data = response.data;
    console.log('[fetchConfig] Response received:', { status: response.status, data });
    
    // The backend returns ConfigResponse which is { config: {...} }
    // Accept both formats: { config: {...} } or just the config object
    if (data && typeof data === 'object') {
      // If it has a 'config' property, return as-is
      if ('config' in data) {
        // Ensure config is an object, not null/undefined
        if (data.config && typeof data.config === 'object') {
          console.log('[fetchConfig] Valid config structure with config property');
          return data;
        }
        // If config is missing or invalid, return default structure
        console.warn('[fetchConfig] Config property exists but is invalid:', data.config);
        return { 
          config: {
            detection: {},
            strategy: { type: 'even_odd', base_bet: 10.0, max_gales: 6, multiplier: 1.75, streak_length: 2, zero_policy: 'neutral', keepalive_stake: 1.0 },
            betting: {},
            table: {},
            session: { maintenance_bet_interval: 1800, min_bet_amount: 1.0 },
            risk: { initial_balance: 1000.0, stop_loss: 500.0, guarantee_fund_percentage: 20 },
            logging: { logs_dir: 'logs', log_level: 'INFO' }
          }
        };
      }
      // If it's the config object directly, wrap it
      if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
        console.log('[fetchConfig] Wrapping config object');
        return { config: data };
      }
    }
    
    // If data is null/undefined, return default config structure
    if (!data) {
      console.warn('[fetchConfig] Config response is empty, returning default config structure');
      return { 
        config: {
          detection: {},
          strategy: { type: 'even_odd', base_bet: 10.0, max_gales: 6, multiplier: 1.75, streak_length: 2, zero_policy: 'neutral', keepalive_stake: 1.0 },
          betting: {},
          table: {},
          session: { maintenance_bet_interval: 1800, min_bet_amount: 1.0 },
          risk: { initial_balance: 1000.0, stop_loss: 500.0, guarantee_fund_percentage: 20 },
          logging: { logs_dir: 'logs', log_level: 'INFO' }
        }
      };
    }
    
    console.error('[fetchConfig] Invalid config response format:', data);
    throw new Error('Invalid config response format');
  } catch (error) {
    console.error('[fetchConfig] Error caught:', error);
    console.error('[fetchConfig] Error message:', error.message);
    console.error('[fetchConfig] Error response:', error.response);
    console.error('[fetchConfig] Error response data:', error.response?.data);
    console.error('[fetchConfig] Error response status:', error.response?.status);
    console.error('[fetchConfig] API base URL:', api.defaults.baseURL);
    
    // Check if it's a network error (no response)
    if (!error.response) {
      console.error('[fetchConfig] Network error - no response received. Possible causes:');
      console.error('  - Backend not accessible at:', api.defaults.baseURL);
      console.error('  - CORS error (check Network tab)');
      console.error('  - Network connectivity issue');
      console.error('  - ngrok not running or URL changed');
    } else {
      console.error('[fetchConfig] HTTP error:', error.response.status, error.response.statusText);
    }
    
    // Return default config structure instead of throwing to prevent UI breaking
    console.warn('[fetchConfig] Returning default config structure due to error');
    return { 
      config: {
        detection: {},
        strategy: { type: 'even_odd', base_bet: 10.0, max_gales: 6, multiplier: 1.75, streak_length: 2, zero_policy: 'neutral', keepalive_stake: 1.0 },
        betting: {},
        table: {},
        session: { maintenance_bet_interval: 1800, min_bet_amount: 1.0 },
        risk: { initial_balance: 1000.0, stop_loss: 500.0, guarantee_fund_percentage: 20 },
        logging: { logs_dir: 'logs', log_level: 'INFO' }
      }
    };
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
  try {
    const { data } = await api.get('/api/config/presets');
    console.log('fetchPresets response:', data);
    
    // Backend returns List[PresetSummary] which should be an array
    // Ensure we always return an array
    if (Array.isArray(data)) {
      return data;
    }
    
    // If data is not an array, return empty array
    console.warn('Presets response is not an array, returning empty array:', data);
    return [];
  } catch (error) {
    console.error('fetchPresets error:', error);
    console.error('Response:', error.response?.data);
    // Return empty array instead of throwing
    return [];
  }
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
  console.log('[stopBot] Sending stop request to:', api.defaults.baseURL + '/api/bot/stop');
  try {
    const response = await api.post('/api/bot/stop');
    console.log('[stopBot] Stop request successful:', response.status, response.data);
    return response.data;
  } catch (error) {
    console.error('[stopBot] Stop request failed:', error);
    console.error('[stopBot] Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config,
    });
    throw error;
  }
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


