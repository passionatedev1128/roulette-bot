import React, { useCallback, useMemo } from 'react';
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

  const statusQuery = useQuery({ queryKey: ['status'], queryFn: fetchStatus, refetchInterval: 5000 });
  const balanceQuery = useQuery({ queryKey: ['balance'], queryFn: fetchBalance, refetchInterval: 5000 });
  const resultsQuery = useQuery({ queryKey: ['results'], queryFn: () => fetchResults(20), refetchInterval: 10000 });
  const activeBetQuery = useQuery({ queryKey: ['activeBet'], queryFn: fetchActiveBet, refetchInterval: 7000 });
  const betHistoryQuery = useQuery({ queryKey: ['betHistory'], queryFn: () => fetchBetHistory(25), refetchInterval: 15000 });
  const configQuery = useQuery({ queryKey: ['config'], queryFn: fetchConfig });
  const presetsQuery = useQuery({ queryKey: ['presets'], queryFn: fetchPresets, staleTime: 60000 });
  const dailyStatsQuery = useQuery({ queryKey: ['dailyStats'], queryFn: fetchDailyStats, refetchInterval: 60000 });
  const strategyStatsQuery = useQuery({ queryKey: ['strategyStats'], queryFn: fetchStrategyStats, refetchInterval: 60000 });
  const galeStatsQuery = useQuery({ queryKey: ['galeStats'], queryFn: fetchGaleStats, refetchInterval: 60000 });

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
            const updated = [...base, newEntry].slice(-20);
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
        const entry = {
          spin_number: event.payload?.spin_number,
          bet_type: event.payload?.bet_type,
          bet_amount: event.payload?.bet_amount ?? 0,
          result: event.payload?.result,
          profit_loss: event.payload?.profit_loss ?? 0,
          balance_after: event.payload?.balance ?? 0,
          timestamp: event.payload?.timestamp ?? new Date().toISOString(),
        };
        queryClient.setQueryData(['betHistory'], (old) => {
          const base = old?.bets ?? [];
          const updated = [...base, entry].slice(-25);
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
        console.error('Bot error', event.payload);
        break;
      default:
        break;
    }
  }, [queryClient]);

  useWebSocket(WS_EVENTS_URL, handleEvent);

  const onSaveConfig = (config) => updateConfigMutation.mutate(config);
  const onSavePreset = (name, config) => {
    if (!name) return;
    savePresetMutation.mutate({ name, config });
  };
  const onLoadPreset = (slug) => {
    if (!slug) return;
    loadPresetMutation.mutate(slug);
  };

  const onStartBot = ({ mode, testMode }) => startBotMutation.mutate({ mode, testMode });
  const onStopBot = () => stopBotMutation.mutate();
  const onModeChange = (mode) => modeMutation.mutate(mode);

  const presets = useMemo(() => presetsQuery.data ?? [], [presetsQuery.data]);

  return (
    <div className="app">
      <StatusBar statusData={statusQuery.data} />

      <div className="dashboard-grid">
        <div className="panel" style={{ gridColumn: '1 / -1' }}>
          <BalanceCards balance={balanceQuery.data} />
        </div>
        <LiveResults results={resultsQuery.data} />
        <ActiveBetsPanel activeBet={activeBetQuery.data} />
        <BetHistoryTable history={betHistoryQuery.data} />
      </div>

      <PerformanceCharts
        dailyStats={dailyStatsQuery.data}
        strategyStats={strategyStatsQuery.data}
        galeStats={galeStatsQuery.data}
      />

      <ModeControls
        statusData={statusQuery.data}
        onStart={onStartBot}
        onStop={onStopBot}
        onModeChange={onModeChange}
        starting={startBotMutation.isLoading}
        stopping={stopBotMutation.isLoading}
      />

      <ConfigForm
        configData={configQuery.data}
        onSave={onSaveConfig}
        saving={updateConfigMutation.isLoading}
        presets={presets}
        onSavePreset={onSavePreset}
        onLoadPreset={onLoadPreset}
      />
    </div>
  );
};

export default App;


