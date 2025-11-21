import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

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
  const { data } = await api.get('/api/config/');
  return data;
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

export const WS_EVENTS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/events';


