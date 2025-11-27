import React from 'react';

const statusColors = {
  running: '#10b981',
  idle: '#d1d5db',
  error: '#ef4444',
};

const statusLabels = {
  running: 'Em execução',
  idle: 'Inativo',
  error: 'Erro',
};

const modeLabels = {
  'Maintenance Mode': 'Modo de manutenção',
  'Full Auto Mode': 'Modo totalmente automático',
  'Manual Analysis Mode': 'Modo de análise manual',
};

const formatDate = (value) => {
  if (!value) {
    return '—';
  }
  const date = typeof value === 'string' ? new Date(value) : value;
  return date.toLocaleString('pt-BR');
};

const formatProcessTime = (seconds) => {
  if (seconds === null || seconds === undefined) {
    return '—';
  }
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};

const StatusBar = ({ statusData, wsConnectionStatus, apiConnectionStatus }) => {
  const status = statusData?.status ?? 'idle';
  const color = statusColors[status] || '#3b82f6';
  const isRunning = status === 'running';
  const statusText = statusLabels[status] || status.toUpperCase();

  // Connection status colors and labels
  // WebSocket uses English labels: "Connected" and "Offline"
  const getWebSocketStatusInfo = (connectionStatus) => {
    switch (connectionStatus) {
      case 'connected':
        return { label: 'Connected', color: '#10b981' };
      case 'connecting':
        return { label: 'Connecting...', color: '#f59e0b' };
      case 'disconnected':
        return { label: 'Offline', color: '#ef4444' };
      default:
        return { label: 'Offline', color: '#9ca3af' };
    }
  };

  // API REST uses Portuguese labels (keep existing behavior)
  const getAPIConnectionStatusInfo = (connectionStatus) => {
    switch (connectionStatus) {
      case 'connected':
        return { label: 'Conectado', color: '#10b981' };
      case 'connecting':
        return { label: 'Conectando...', color: '#f59e0b' };
      case 'disconnected':
        return { label: 'Desconectado', color: '#ef4444' };
      default:
        return { label: 'Desconhecido', color: '#9ca3af' };
    }
  };

  const wsStatus = getWebSocketStatusInfo(wsConnectionStatus);
  const apiStatus = getAPIConnectionStatusInfo(apiConnectionStatus);

  return (
    <div className="status-bar">
      <div className="status-chip" style={{ backgroundColor: color }} />
      <div className="status-text">
        <span className="status-label">Estado</span>
        <strong style={{ 
          color: color,
          textShadow: isRunning ? `0 0 10px ${color}` : 'none'
        }}>
          {statusText}
        </strong>
      </div>
      <div className="status-text">
        <span className="status-label">WebSocket</span>
        <strong style={{ color: wsStatus.color }}>
          {wsStatus.label}
        </strong>
      </div>
      <div className="status-text">
        <span className="status-label">API REST</span>
        <strong style={{ color: apiStatus.color }}>
          {apiStatus.label}
        </strong>
      </div>
      <div className="status-text">
        <span className="status-label">Modo</span>
        <strong>{modeLabels[statusData?.mode] || statusData?.mode || '—'}</strong>
      </div>
      <div className="status-text">
        <span className="status-label">Giros</span>
        <strong>{statusData?.spin_number ?? 0}</strong>
      </div>
      <div className="status-text">
        <span className="status-label">Última atividade</span>
        <strong>{formatDate(statusData?.last_activity)}</strong>
      </div>
      {isRunning && statusData?.process_time_seconds !== null && statusData?.process_time_seconds !== undefined && (
        <div className="status-text">
          <span className="status-label">Tempo de execução</span>
          <strong>{formatProcessTime(statusData.process_time_seconds)}</strong>
        </div>
      )}
    </div>
  );
};

export default StatusBar;


