import React, { useCallback, useMemo, useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  WS_EVENTS_URL,
  changeMode,
  fetchActiveBet,
  fetchBalance,
  fetchBetHistory,
  fetchConfig,
  fetchDailyStats,
  fetchGaleStats,
  fetchPresets,
  fetchResults,
  fetchStatus,
  fetchStrategyStats,
  loadPreset,
  savePreset,
  startBot,
  stopBot,
  updateConfig,
} from './api/client.js';
import { useWebSocket } from './hooks/useWebSocket.js';
import { isDemoMode, mockData, startMockUpdates, stopMockUpdates } from './utils/mockData.js';
import StatusBar from './components/StatusBar.jsx';
import BalanceCards from './components/BalanceCards.jsx';
import LiveResults from './components/LiveResults.jsx';
import ActiveBetsPanel from './components/ActiveBetsPanel.jsx';
import BetHistoryTable from './components/BetHistoryTable.jsx';
import PerformanceCharts from './components/PerformanceCharts.jsx';
import ConfigForm from './components/ConfigForm.jsx';
import ModeControls from './components/ModeControls.jsx';

const App = () => {
  const queryClient = useQueryClient();
  // Check URL parameter on mount
  const [demoMode, setDemoMode] = useState(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('demo') === 'true') {
      localStorage.setItem('demoMode', 'true');
      console.log('Demo mode enabled via URL parameter');
      return true;
    }
    const isDemo = isDemoMode();
    console.log('Demo mode check:', { isDemo, localStorage: localStorage.getItem('demoMode'), urlParam: urlParams.get('demo') });
    return isDemo;
  });
  
  // Log API calls status
  useEffect(() => {
    console.log('App initialized:', {
      demoMode,
      willMakeAPICalls: !demoMode,
      API_BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    });
  }, [demoMode]);

  // Track bot start time for process time calculation
  const [botStartTime, setBotStartTime] = useState(null);
  
  // Initialize mock data in demo mode
  useEffect(() => {
    if (demoMode) {
      // Set initial mock data
      queryClient.setQueryData(['status'], mockData.status());
      queryClient.setQueryData(['balance'], mockData.balance());
      queryClient.setQueryData(['results'], mockData.results(20));
      queryClient.setQueryData(['activeBet'], mockData.activeBet());
      queryClient.setQueryData(['betHistory'], mockData.betHistory(25));
      queryClient.setQueryData(['config'], mockData.config());
      queryClient.setQueryData(['presets'], mockData.presets());
      queryClient.setQueryData(['dailyStats'], mockData.dailyStats());
      queryClient.setQueryData(['strategyStats'], mockData.strategyStats());
      queryClient.setQueryData(['galeStats'], mockData.galeStats());
      
      // Start periodic updates
      startMockUpdates((eventType, payload) => {
        if (eventType === 'new_result') {
          const newEntry = {
            spin_number: (queryClient.getQueryData(['status'])?.spin_number || 156) + 1,
            number: payload.spin_data.number,
            color: payload.spin_data.color,
            zero: payload.spin_data.number === 0,
            timestamp: new Date().toISOString(),
          };
          queryClient.setQueryData(['results'], (old) => {
            const base = old?.results ?? [];
            const updated = [newEntry, ...base].slice(0, 20);
            return { results: updated };
          });
          queryClient.setQueryData(['status'], (old) => ({
            ...old,
            spin_number: newEntry.spin_number,
            last_activity: new Date().toISOString(),
          }));
        }
      });
    }
    
    return () => {
      if (demoMode) {
        stopMockUpdates();
      }
    };
  }, [demoMode, queryClient]);

  // Use mock data functions in demo mode, otherwise use real API
  const statusQuery = useQuery({ 
    queryKey: ['status'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.status()) : fetchStatus, 
    refetchInterval: demoMode ? false : 5000,
    enabled: true, // Always enabled, but uses mock data in demo mode
    onError: (error) => {
      console.error('Failed to fetch status:', error);
    },
  });
  
  // Update process time periodically while bot is running
  useEffect(() => {
    const status = statusQuery.data;
    if (status?.running && !botStartTime) {
      // Bot just started, record start time
      setBotStartTime(Date.now());
    } else if (!status?.running && botStartTime) {
      // Bot stopped, clear start time
      setBotStartTime(null);
    }
  }, [statusQuery.data?.running, botStartTime]);
  
  // Update process time in status data every second while running
  useEffect(() => {
    if (!botStartTime || !statusQuery.data?.running) {
      return;
    }
    
    const interval = setInterval(() => {
      const elapsedSeconds = Math.floor((Date.now() - botStartTime) / 1000);
      queryClient.setQueryData(['status'], (old) => ({
        ...old,
        process_time_seconds: elapsedSeconds
      }));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [botStartTime, statusQuery.data?.running, queryClient]);
  
  const balanceQuery = useQuery({ 
    queryKey: ['balance'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.balance()) : fetchBalance, 
    refetchInterval: demoMode ? false : 5000,
    enabled: true,
    onError: (error) => {
      console.error('Failed to fetch balance:', error);
    },
  });
  
  const resultsQuery = useQuery({ 
    queryKey: ['results'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.results(20)) : () => fetchResults(20), 
    refetchInterval: demoMode ? false : 10000,
    enabled: true,
    onError: (error) => {
      console.error('Failed to fetch results:', error);
    },
  });
  
  const activeBetQuery = useQuery({ 
    queryKey: ['activeBet'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.activeBet()) : fetchActiveBet, 
    refetchInterval: demoMode ? false : 7000,
    enabled: true,
    // Don't refetch if we have data set via setQueryData (staleTime prevents unnecessary refetches)
    staleTime: 5000, // Consider data fresh for 5 seconds
    // Don't overwrite data set via setQueryData with null from API
    placeholderData: (previousData) => previousData,
    // Ensure component re-renders when query data changes
    notifyOnChangeProps: ['data', 'isSuccess'],
    onError: (error) => {
      console.error('Failed to fetch active bet:', error);
    },
    onSuccess: (data) => {
      console.log('[Active Bet Query] Fetched from API:', data);
      // Only update if we got valid data (not null) AND we don't already have WebSocket data
      // If API returns null, don't overwrite data that was set via WebSocket events
      const currentData = queryClient.getQueryData(['activeBet']);
      console.log('[Active Bet Query] Current data in cache:', currentData);
      if (data !== null && !currentData) {
        // API returned valid data and we have no WebSocket data, use API data
        console.log('[Active Bet Query] Using API data:', data);
        queryClient.setQueryData(['activeBet'], data);
      } else if (data !== null && currentData && !currentData._updated) {
        // API returned valid data and current data doesn't have _updated (from API), use API data
        console.log('[Active Bet Query] Replacing API data with new API data:', data);
        queryClient.setQueryData(['activeBet'], data);
      } else if (data === null && currentData) {
        // API returned null but we have data from WebSocket, keep the WebSocket data
        console.log('[Active Bet Query] API returned null, keeping WebSocket data:', currentData);
        // Don't update - keep the existing data
      } else if (data === null && !currentData) {
        // API returned null and we have no data, set to null
        console.log('[Active Bet Query] API returned null, no current data, setting to null');
        queryClient.setQueryData(['activeBet'], null);
      }
    },
  });
  
  const statusRunning = statusQuery.data?.running === true;
  const betHistoryQuery = useQuery({ 
    queryKey: ['betHistory'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.betHistory(25)) : () => fetchBetHistory(25), 
    refetchInterval: demoMode ? false : (statusRunning ? 5000 : 15000), // Refresh more frequently when bot is running
  });
  
  const configQuery = useQuery({ 
    queryKey: ['config'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.config()) : fetchConfig,
    enabled: !demoMode, // Only enable if not in demo mode
    retry: 3,
    retryDelay: 1000,
    onError: (error) => {
      console.error('Failed to fetch config:', error);
    },
    onSuccess: (data) => {
      console.log('Config fetched successfully:', data);
    },
  });
  
  const presetsQuery = useQuery({ 
    queryKey: ['presets'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.presets()) : fetchPresets, 
    staleTime: 60000,
  });
  
  const dailyStatsQuery = useQuery({ 
    queryKey: ['dailyStats'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.dailyStats()) : fetchDailyStats, 
    refetchInterval: demoMode ? false : 60000,
  });
  
  const strategyStatsQuery = useQuery({ 
    queryKey: ['strategyStats'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.strategyStats()) : fetchStrategyStats, 
    refetchInterval: demoMode ? false : 60000,
  });

  // Clear "Desempenho por estratégia" contents when system/app starts (non-demo mode)
  useEffect(() => {
    if (!demoMode) {
      queryClient.setQueryData(['strategyStats'], { stats: [] });
    }
  }, [demoMode, queryClient]);
  
  const galeStatsQuery = useQuery({ 
    queryKey: ['galeStats'], 
    queryFn: demoMode ? () => Promise.resolve(mockData.galeStats()) : fetchGaleStats, 
    refetchInterval: demoMode ? false : 60000,
  });

  const updateConfigMutation = useMutation({
    mutationFn: (params) => {
      // Handle both object format { config, persist } and direct config format
      if (params && typeof params === 'object' && params.config !== undefined) {
        // New format: { config, persist }
        return updateConfig(params.config, params.persist !== undefined ? params.persist : true);
      }
      // Old format: just config object (for backward compatibility)
      return updateConfig(params, true);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['config'], data);
      queryClient.invalidateQueries(['balance']);
    },
  });

  const savePresetMutation = useMutation({
    mutationFn: ({ name, config }) => savePreset(name, config),
    onSuccess: () => {
      queryClient.invalidateQueries(['presets']);
    },
  });

  const loadPresetMutation = useMutation({
    mutationFn: (slug) => loadPreset(slug),
    onSuccess: (data) => {
      queryClient.setQueryData(['config'], data);
    },
  });

  const startBotMutation = useMutation({
    mutationFn: (payload) => startBot(payload),
    onSuccess: (data) => {
      queryClient.setQueryData(['status'], data);
      // Empty "Desempenho por estratégia" contents when bot starts
      queryClient.setQueryData(['strategyStats'], { stats: [] });
      // Clear "Resultados ao vivo" table when bot starts
      queryClient.setQueryData(['results'], { results: [] });
      // Keep "Desempenho diário" (dailyStats) and "Desempenho por gale" (galeStats) - DO NOT RESET
      // Clear "Histórico de apostas" (Bet History) table when bot starts
      queryClient.setQueryData(['betHistory'], { bets: [] });
      // Invalidate queries to refresh data when bot starts (but keep strategyStats empty)
      queryClient.invalidateQueries(['betHistory']);
      queryClient.invalidateQueries(['activeBet']);
      queryClient.invalidateQueries(['balance']);
      // Cancel any pending strategyStats refetches to keep it empty
      queryClient.cancelQueries(['strategyStats']);
      // Record bot start time for process time calculation
      setBotStartTime(Date.now());
    },
  });

  const stopBotMutation = useMutation({
    mutationFn: stopBot,
    onSuccess: (data) => {
      console.log('[Stop Bot] Success:', data);
      queryClient.setQueryData(['status'], data);
      queryClient.invalidateQueries(['activeBet']);
    },
    onError: (error) => {
      console.error('[Stop Bot] Error:', error);
      console.error('[Stop Bot] Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config,
      });
      // Show user-friendly error message
      alert(`Failed to stop bot: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    },
  });

  const modeMutation = useMutation({
    mutationFn: (mode) => changeMode(mode),
    onSuccess: (data) => {
      queryClient.setQueryData(['status'], data);
    },
  });

  const handleEvent = useCallback((event) => {
    // Access botStartTime from closure - will be updated by state
    if (!event?.type) {
      return;
    }
    switch (event.type) {
      case 'status_change': {
        const isRunning = event.payload?.status === 'running' || event.payload?.running === true;
        // Update performance stats periodically while bot is running
        if (isRunning) {
          queryClient.invalidateQueries(['dailyStats']);
          queryClient.invalidateQueries(['galeStats']);
        }
        queryClient.setQueryData(['status'], (old) => ({ ...(old ?? {}), ...event.payload, running: isRunning }));
        break;
      }
      case 'balance_update':
        queryClient.setQueryData(['balance'], (old) => {
          if (!old) {
            return old;
          }
          const balance = event.payload?.balance ?? old.current_balance;
          const initial = old.initial_balance ?? 0;
          return {
            ...old,
            current_balance: balance,
            profit_loss: balance - initial,
          };
        });
        break;
      case 'new_result': {
        const resultPayload = event.payload?.spin_data;
        if (resultPayload) {
          const newEntry = {
            spin_number: resultPayload.spin_number,
            number: resultPayload.outcome_number,
            color: resultPayload.outcome_color,
            zero: resultPayload.outcome_number === 0,
            timestamp: resultPayload.timestamp,
          };
          queryClient.setQueryData(['results'], (old) => {
            const base = old?.results ?? [];
            // Check if this result already exists (same spin_number and number) to prevent duplicates
            const exists = base.some(
              (item) => item.spin_number === newEntry.spin_number && 
                       item.number === newEntry.number
            );
            if (exists) {
              // Duplicate detected, don't add it
              return old;
            }
            const updated = [newEntry, ...base].slice(0, 20); // Add to beginning, keep latest 20
            return { results: updated };
          });
        }
        if (event.payload?.bet_decision) {
          // Update active bet when decision is made (before placement)
          queryClient.setQueryData(['activeBet'], {
            bet_type: event.payload.bet_decision.bet_type,
            bet_amount: event.payload.bet_decision.bet_amount,
            gale_step: event.payload.gale_step,
            placed_at: new Date().toISOString(),
          });
          // Refresh active bet query
          queryClient.invalidateQueries(['activeBet']);
          queryClient.refetchQueries(['activeBet'], { exact: true });
          // Refresh stats when bet decision is made (pre-bet placement)
          queryClient.invalidateQueries(['dailyStats']);
          queryClient.invalidateQueries(['galeStats']);
          queryClient.invalidateQueries(['strategyStats']);
          // Refetch stats to show pending bet state
          queryClient.refetchQueries(['dailyStats'], { exact: true });
          queryClient.refetchQueries(['galeStats'], { exact: true });
        }
        break;
      }
      case 'bet_placed': {
        // Update active bet immediately with data from event
        const betPlacedData = {
          bet_type: event.payload?.bet_type,
          bet_amount: event.payload?.bet_amount,
          gale_step: event.payload?.gale_step,
          placed_at: event.payload?.timestamp || new Date().toISOString(),
        };
        console.log('[Active Bet] bet_placed event received:', betPlacedData);
        // Ensure all values are properly set
        const updatedData = {
          bet_type: betPlacedData.bet_type || null,
          bet_amount: betPlacedData.bet_amount || null,
          gale_step: betPlacedData.gale_step ?? null,
          placed_at: betPlacedData.placed_at || null,
          _updated: Date.now() // Mark as updated via WebSocket to prevent API overwrite
        };
        console.log('[Active Bet] Setting query data with:', updatedData);
        // Set query data immediately - this will trigger UI update
        queryClient.setQueryData(['activeBet'], updatedData);
        // Verify the data was set immediately
        const verifyData = queryClient.getQueryData(['activeBet']);
        console.log('[Active Bet] Verified query data after set:', verifyData);
        // Force React Query to notify all subscribers (without refetching)
        queryClient.invalidateQueries(['activeBet'], { refetchType: 'none' });
        // Cancel any pending refetches to avoid overwriting with stale API data
        queryClient.cancelQueries(['activeBet']);
        // Verify the data was set after cancel
        const verifyDataAfterCancel = queryClient.getQueryData(['activeBet']);
        console.log('[Active Bet] Verified query data after cancel:', verifyDataAfterCancel);
        // Update performance stats after betting - invalidate and refetch immediately
        queryClient.invalidateQueries(['dailyStats']);
        queryClient.invalidateQueries(['galeStats']);
        queryClient.invalidateQueries(['strategyStats']);
        // Force refetch stats immediately for real-time updates (with small delay to ensure CSV is updated)
        setTimeout(() => {
        queryClient.refetchQueries(['dailyStats'], { exact: true });
        queryClient.refetchQueries(['galeStats'], { exact: true });
        queryClient.refetchQueries(['strategyStats'], { exact: true });
        }, 100);
        break;
      }
      case 'bet_resolved': {
        // Clear active bet immediately
        queryClient.setQueryData(['activeBet'], null);
        // Force refresh active bet query to ensure UI clears properly
        queryClient.invalidateQueries(['activeBet']);
        queryClient.refetchQueries(['activeBet'], { exact: true });
        // Create bet history entry with real data from event
        const entry = {
          spin_number: event.payload?.spin_number ?? 0,
          bet_type: event.payload?.bet_type ?? 'unknown',
          bet_amount: event.payload?.bet_amount ?? 0,
          result: event.payload?.result ?? 'unknown',
          profit_loss: event.payload?.profit_loss ?? 0,
          balance_after: event.payload?.balance ?? 0,
          timestamp: event.payload?.timestamp ?? new Date().toISOString(),
        };
        queryClient.setQueryData(['betHistory'], (old) => {
          const base = old?.bets ?? [];
          // Check if this entry already exists (same spin_number) to prevent duplicates
          const exists = base.some(
            (item) => item.spin_number === entry.spin_number
          );
          if (exists) {
            // Duplicate detected, don't add it
            console.log(`[Betting History] Duplicate entry ignored for spin #${entry.spin_number}`);
            return old;
          }
          // Add new entry to the beginning and keep latest 25
          const updated = [entry, ...base].slice(0, 25);
          console.log(
            `[Betting History] New entry added to table: Spin #${entry.spin_number}, ` +
            `Bet: ${entry.bet_type} ${entry.bet_amount}, Result: ${entry.result}, ` +
            `P/L: ${entry.profit_loss >= 0 ? '+' : ''}${entry.profit_loss}, ` +
            `Total entries: ${updated.length}`
          );
          return { bets: updated           };
        });
        queryClient.setQueryData(['balance'], (old) => {
          if (!old) {
            return old;
          }
          const balance = event.payload?.balance ?? old.current_balance;
          const initial = old.initial_balance ?? 0;
          return {
            ...old,
            current_balance: balance,
            profit_loss: balance - initial,
          };
        });
        // Update performance stats after bet is resolved (win/loss)
        queryClient.invalidateQueries(['dailyStats']);
        queryClient.invalidateQueries(['galeStats']);
        queryClient.invalidateQueries(['strategyStats']);
        // Force refetch stats immediately for better UX (with small delay to ensure CSV is updated)
        setTimeout(() => {
        queryClient.refetchQueries(['dailyStats'], { exact: true });
        queryClient.refetchQueries(['galeStats'], { exact: true });
        queryClient.refetchQueries(['strategyStats'], { exact: true });
        }, 100);
        break;
      }
      case 'error':
        console.error('Erro do bot', event.payload);
        break;
      default:
        break;
    }
  }, [queryClient]);

  // Track WebSocket connection status
  const { connectionStatus: wsConnectionStatus } = useWebSocket(demoMode ? null : WS_EVENTS_URL, handleEvent);
  
  // Track REST API connection status
  const [apiConnectionStatus, setApiConnectionStatus] = useState('unknown'); // 'connected', 'disconnected', 'unknown'
  
  // Monitor API connection status by checking if status query succeeds/fails
  useEffect(() => {
    if (demoMode) {
      setApiConnectionStatus('connected');
      return;
    }
    
    if (statusQuery.isSuccess) {
      setApiConnectionStatus('connected');
    } else if (statusQuery.isError) {
      setApiConnectionStatus('disconnected');
    } else {
      setApiConnectionStatus('unknown');
    }
  }, [statusQuery.isSuccess, statusQuery.isError, demoMode]);

  const onSaveConfig = (config) => {
    if (demoMode) {
      // In demo mode, just update local state
      queryClient.setQueryData(['config'], { config });
      alert('Configuração salva (Modo Demo)');
    } else {
      // Explicitly save with persist=true to save to default_config.json
      updateConfigMutation.mutate({ config, persist: true });
    }
  };
  const onSavePreset = (name, config) => {
    if (!name) return;
    savePresetMutation.mutate({ name, config });
  };
  const onLoadPreset = (slug) => {
    if (!slug) return;
    loadPresetMutation.mutate(slug);
  };

  const onStartBot = ({ mode, testMode }) => {
    if (demoMode) {
      // In demo mode, just update local state
      queryClient.setQueryData(['status'], {
        running: true,
        status: 'running',
        mode: mode || 'Full Auto Mode',
        last_activity: new Date().toISOString(),
        spin_number: queryClient.getQueryData(['status'])?.spin_number || 156,
      });
    } else {
      startBotMutation.mutate({ mode, testMode });
    }
  };
  
  const onStopBot = () => {
    if (demoMode) {
      queryClient.setQueryData(['status'], {
        running: false,
        status: 'idle',
        mode: queryClient.getQueryData(['status'])?.mode || 'Full Auto Mode',
        last_activity: new Date().toISOString(),
        spin_number: queryClient.getQueryData(['status'])?.spin_number || 156,
      });
      queryClient.setQueryData(['activeBet'], null);
    } else {
      stopBotMutation.mutate();
    }
  };
  
  const onModeChange = (mode) => {
    if (demoMode) {
      queryClient.setQueryData(['status'], (old) => ({
        ...old,
        mode: mode,
      }));
    } else {
      modeMutation.mutate(mode);
    }
  };

  const presets = useMemo(() => {
    const data = presetsQuery.data;
    // Ensure presets is always an array
    if (Array.isArray(data)) {
      return data;
    }
    // If data is not an array, return empty array
    if (data !== null && data !== undefined) {
      console.warn('Presets data is not an array:', data);
    }
    return [];
  }, [presetsQuery.data]);

  const enableDemoMode = () => {
    localStorage.setItem('demoMode', 'true');
    setDemoMode(true);
    // Force reload to initialize all data
    window.location.reload();
  };

  return (
    <div className="app">
      {demoMode && (
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '12px 24px',
          borderRadius: '8px',
          marginBottom: '16px',
          textAlign: 'center',
          fontWeight: 600,
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        }}>
          🎭 MODO DEMO - Exibindo dados simulados | 
          <button 
            onClick={() => {
              localStorage.removeItem('demoMode');
              window.location.href = window.location.pathname;
            }}
            style={{
              marginLeft: '12px',
              padding: '4px 12px',
              background: 'rgba(255,255,255,0.2)',
              border: '1px solid rgba(255,255,255,0.3)',
              borderRadius: '4px',
              color: 'white',
              cursor: 'pointer',
            }}
          >
            Sair do demo
          </button>
        </div>
      )}
      <StatusBar 
        statusData={statusQuery.data} 
        wsConnectionStatus={demoMode ? 'connected' : wsConnectionStatus}
        apiConnectionStatus={demoMode ? 'connected' : apiConnectionStatus}
      />

      <div className="dashboard-grid">
        <div className="panel" style={{ gridColumn: '1 / -1' }}>
          <BalanceCards balance={balanceQuery.data} />
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <BetHistoryTable history={betHistoryQuery.data} />
        </div>
      </div>

      <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        <PerformanceCharts
          dailyStats={dailyStatsQuery.data}
          strategyStats={strategyStatsQuery.data}
          galeStats={galeStatsQuery.data}
        />
        <ActiveBetsPanel activeBet={activeBetQuery.data} />
      </div>

      <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr' }}>
        <LiveResults results={resultsQuery.data} />
      </div>

      <div className="panel" style={{ marginBottom: 'var(--spacing-xl)' }}>
        <div className="panel-header">
          <h2>Desempenho por estratégia</h2>
          <span className="panel-subtitle">Taxa de acerto por estratégia</span>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Estratégia</th>
                <th>Apostas</th>
                <th>Vitórias</th>
                <th>Derrotas</th>
                <th>Taxa de acerto</th>
                <th>P/L</th>
              </tr>
            </thead>
            <tbody>
              {strategyStatsQuery.data?.stats && Array.isArray(strategyStatsQuery.data.stats) && strategyStatsQuery.data.stats.length > 0 ? (
                strategyStatsQuery.data.stats.map((row) => (
                  <tr key={row.strategy}>
                    <td>{row.strategy}</td>
                    <td>{row.bets}</td>
                    <td>{row.wins}</td>
                    <td>{row.losses}</td>
                    <td style={{ fontWeight: 600 }}>{row.win_rate}%</td>
                    <td style={{ 
                      color: row.profit_loss >= 0 ? '#10b981' : '#ef4444',
                      fontWeight: 600
                    }}>
                      {row.profit_loss >= 0 ? '+' : ''}{row.profit_loss.toFixed(2)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="empty-state">Nenhum dado de estratégia ainda.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ marginBottom: 'var(--spacing-xl)' }}>
          <ModeControls
            statusData={statusQuery.data}
            onStart={onStartBot}
            onStop={onStopBot}
            onModeChange={onModeChange}
            starting={startBotMutation.isLoading}
            stopping={stopBotMutation.isLoading}
            wsConnectionStatus={demoMode ? 'connected' : wsConnectionStatus}
            apiConnectionStatus={demoMode ? 'connected' : apiConnectionStatus}
          />
      </div>

      {configQuery.isLoading && (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          Carregando configuração...
        </div>
      )}
      {configQuery.isError && (
        <div style={{ 
          padding: '20px', 
          margin: '20px', 
          background: '#fee', 
          border: '1px solid #fcc', 
          borderRadius: '8px',
          color: '#c33'
        }}>
          <strong>Erro ao carregar configuração:</strong> {configQuery.error?.message || 'Erro desconhecido'}
          <button 
            onClick={() => configQuery.refetch()}
            style={{
              marginLeft: '10px',
              padding: '5px 15px',
              background: '#c33',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Tentar novamente
          </button>
        </div>
      )}
      {!configQuery.isLoading && !configQuery.isError && (
        <ConfigForm
          configData={configQuery.data}
          onSave={onSaveConfig}
          saving={updateConfigMutation.isLoading}
          presets={presets}
          onSavePreset={onSavePreset}
          onLoadPreset={onLoadPreset}
          isBotRunning={statusQuery.data?.running === true}
        />
      )}
    </div>
  );
};

export default App;


