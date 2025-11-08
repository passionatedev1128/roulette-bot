import React from 'react';

const formatAmount = (value) => (value !== undefined && value !== null
  ? Number(value).toFixed(2)
  : '—');

const ActiveBetsPanel = ({ activeBet }) => (
  <div className="panel">
    <div className="panel-header">
      <h2>Active Bet</h2>
      <span className="panel-subtitle">Current exposure</span>
    </div>
    {activeBet ? (
      <div className="active-bet">
        <div>
          <span className="label">Bet Type</span>
          <strong>{activeBet.bet_type}</strong>
        </div>
        <div>
          <span className="label">Amount</span>
          <strong>{formatAmount(activeBet.bet_amount)}</strong>
        </div>
        <div>
          <span className="label">Gale Step</span>
          <strong>{activeBet.gale_step ?? '—'}</strong>
        </div>
        <div>
          <span className="label">Placed At</span>
          <strong>{activeBet.placed_at ? new Date(activeBet.placed_at).toLocaleTimeString() : '—'}</strong>
        </div>
      </div>
    ) : (
      <div className="empty-state">No active bet at the moment.</div>
    )}
  </div>
);

export default ActiveBetsPanel;


