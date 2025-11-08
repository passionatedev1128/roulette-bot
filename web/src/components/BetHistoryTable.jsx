import React from 'react';

const formatNumber = (value) => (value !== undefined && value !== null ? Number(value).toFixed(2) : '—');

const BetHistoryTable = ({ history }) => (
  <div className="panel">
    <div className="panel-header">
      <h2>Bet History</h2>
      <span className="panel-subtitle">Latest resolved bets</span>
    </div>
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Spin</th>
            <th>Bet Type</th>
            <th>Amount</th>
            <th>Result</th>
            <th>P/L</th>
            <th>Balance</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {history?.bets?.length ? (
            history.bets.map((bet) => (
              <tr key={`${bet.spin_number}-${bet.timestamp}`}>
                <td>#{bet.spin_number}</td>
                <td>{bet.bet_type ?? '—'}</td>
                <td>{formatNumber(bet.bet_amount)}</td>
                <td className={`result-${bet.result}`}>{bet.result}</td>
                <td>{formatNumber(bet.profit_loss)}</td>
                <td>{formatNumber(bet.balance_after)}</td>
                <td>{new Date(bet.timestamp).toLocaleString()}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={7} className="empty-state">No bet history yet.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  </div>
);

export default BetHistoryTable;


