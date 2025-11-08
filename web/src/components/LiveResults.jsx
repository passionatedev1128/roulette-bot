import React from 'react';

const colorMap = {
  red: '#ef4444',
  black: '#1f2937',
  green: '#10b981',
};

const LiveResults = ({ results }) => (
  <div className="panel">
    <div className="panel-header">
      <h2>Live Results</h2>
      <span className="panel-subtitle">Most recent spins</span>
    </div>
    <div className="results-strip">
      {results?.results?.length ? (
        results.results.map((item) => {
          const color = colorMap[item.color?.toLowerCase()] || '#6b7280';
          return (
            <div key={item.spin_number} className="result-chip" style={{ borderColor: color }}>
              <div className="result-number" style={{ backgroundColor: color }}>
                {item.number ?? '—'}
              </div>
              <span className="result-meta">#{item.spin_number}</span>
            </div>
          );
        })
      ) : (
        <div className="empty-state">Waiting for results…</div>
      )}
    </div>
  </div>
);

export default LiveResults;


