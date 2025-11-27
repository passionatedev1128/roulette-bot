import React from 'react';

const formatAmount = (value) => (value !== undefined && value !== null
  ? new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 2,
    }).format(Number(value))
  : '—');

const ActiveBetsPanel = ({ activeBet }) => (
  <div className="panel">
    <div className="panel-header">
      <h2>Aposta ativa</h2>
      <span className="panel-subtitle">Exposição atual</span>
    </div>
    <div className="active-bet">
      <div>
        <span className="label">Tipo de aposta</span>
        <span className="value" style={{ 
          textTransform: 'uppercase', 
          color: activeBet?.bet_type === 'even' ? '#6366f1' : activeBet?.bet_type === 'odd' ? '#10b981' : '#9ca3af',
          fontWeight: 700
        }}>
          {activeBet?.bet_type || '—'}
        </span>
      </div>
      <div>
        <span className="label">Valor</span>
        <span className="value" style={{ color: activeBet ? '#ef4444' : '#9ca3af', fontWeight: 700 }}>
          {formatAmount(activeBet?.bet_amount)}
        </span>
      </div>
      <div>
        <span className="label">Gale</span>
        <span className="value">{activeBet?.gale_step ?? '—'}</span>
      </div>
      <div>
        <span className="label">Registrada em</span>
        <span className="value" style={{ fontSize: '0.95rem' }}>
          {activeBet?.placed_at ? new Date(activeBet.placed_at).toLocaleTimeString('pt-BR') : '—'}
        </span>
      </div>
    </div>
  </div>
);

export default ActiveBetsPanel;
