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
    onError: (error) => {
      console.error('Failed to fetch active bet:', error);
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
    mutationFn: (config) => updateConfig(config),
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
      // Invalidate queries to refresh data when bot starts (but keep strategyStats empty)
      queryClient.invalidateQueries(['betHistory']);
      queryClient.invalidateQueries(['activeBet']);
      queryClient.invalidateQueries(['balance']);
      queryClient.invalidateQueries(['results']);
      // Cancel any pending strategyStats refetches to keep it empty
      queryClient.cancelQueries(['strategyStats']);
    },
  });

  const stopBotMutation = useMutation({
    mutationFn: stopBot,
    onSuccess: (data) => {
      queryClient.setQueryData(['status'], data);
      queryClient.invalidateQueries(['activeBet']);
    },
  });

  const modeMutation = useMutation({
    mutationFn: (mode) => changeMode(mode),
    onSuccess: (data) => {
      queryClient.setQueryData(['status'], data);
    },
  });

  const handleEvent = useCallback((event) => {
    if (!event?.type) {
      return;
    }
    switch (event.type) {
      case 'status_change':
        queryClient.setQueryData(['status'], (old) => ({ ...(old ?? {}), ...event.payload, running: event.payload?.status === 'running' ? true : event.payload?.running ?? old?.running }));
        break;
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
          queryClient.setQueryData(['activeBet'], {
            bet_type: event.payload.bet_decision.bet_type,
            bet_amount: event.payload.bet_decision.bet_amount,
            gale_step: event.payload.gale_step,
            placed_at: new Date().toISOString(),
          });
        }
        break;
      }
      case 'bet_placed':
        queryClient.setQueryData(['activeBet'], {
          bet_type: event.payload?.bet_type,
          bet_amount: event.payload?.bet_amount,
          gale_step: event.payload?.gale_step,
          placed_at: new Date().toISOString(),
        });
        break;
      case 'bet_resolved': {
        queryClient.setQueryData(['activeBet'], null);
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
          return { bets: updated };
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
        break;
      }
      case 'error':
        console.error('Erro do bot', event.payload);
        break;
      default:
        break;
    }
  }, [queryClient]);

  // Only use WebSocket if not in demo mode
  useWebSocket(demoMode ? null : WS_EVENTS_URL, handleEvent);

  const onSaveConfig = (config) => {
    if (demoMode) {
      // In demo mode, just update local state
      queryClient.setQueryData(['config'], { config });
      alert('Configuração salva (Modo Demo)');
    } else {
      updateConfigMutation.mutate(config);
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
      <StatusBar statusData={statusQuery.data} />

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


