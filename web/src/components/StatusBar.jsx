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

const StatusBar = ({ statusData }) => {
  const status = statusData?.status ?? 'idle';
  const color = statusColors[status] || '#3b82f6';
  const isRunning = status === 'running';
  const statusText = statusLabels[status] || status.toUpperCase();

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
    </div>
  );
};

export default StatusBar;


