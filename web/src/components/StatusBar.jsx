import React from 'react';

const statusColors = {
  running: '#10b981',
  idle: '#d1d5db',
  error: '#ef4444',
};

const formatDate = (value) => {
  if (!value) {
    return '—';
  }
  const date = typeof value === 'string' ? new Date(value) : value;
  return date.toLocaleString();
};

const StatusBar = ({ statusData }) => {
  const status = statusData?.status ?? 'idle';
  const color = statusColors[status] || '#3b82f6';

  return (
    <div className="status-bar">
      <div className="status-chip" style={{ backgroundColor: color }} />
      <div className="status-text">
        <span className="status-label">Status:</span>
        <strong>{status.toUpperCase()}</strong>
      </div>
      <div className="status-text">
        <span className="status-label">Mode:</span>
        <strong>{statusData?.mode || '—'}</strong>
      </div>
      <div className="status-text">
        <span className="status-label">Spins:</span>
        <strong>{statusData?.spin_number ?? 0}</strong>
      </div>
      <div className="status-text">
        <span className="status-label">Last Activity:</span>
        <strong>{formatDate(statusData?.last_activity)}</strong>
      </div>
    </div>
  );
};

export default StatusBar;


