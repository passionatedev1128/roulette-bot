import React from 'react';

const colorMap = {
  red: '#ef4444',
  black: '#1f2937',
  green: '#10b981',
};

const LiveResults = ({ results }) => {
  const resultItems = results?.results || [];
  const latestResult = resultItems[0];
  
  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Resultados ao vivo</h2>
        <span className="panel-subtitle">
          {resultItems.length > 0 
            ? `${resultItems.length} giros recentes` 
            : 'Giros mais recentes'}
        </span>
      </div>
      <div className="results-strip">
        {resultItems.length > 0 ? (
          resultItems.map((item, index) => {
            const color = colorMap[item.color?.toLowerCase()] || '#6b7280';
            const isLatest = index === 0;
            // Use combination of spin_number and number for unique key (prevent duplicates)
            const uniqueKey = `${item.spin_number}-${item.number}`;
            return (
              <div 
                key={uniqueKey} 
                className="result-chip" 
                style={{ 
                  borderColor: color,
                  borderWidth: isLatest ? '3px' : '2px',
                  transform: isLatest ? 'scale(1.05)' : 'scale(1)',
                  boxShadow: isLatest ? `0 0 20px ${color}40` : 'none'
                }}
              >
                <div 
                  className="result-number" 
                  style={{ 
                    backgroundColor: color,
                    boxShadow: isLatest ? `0 0 15px ${color}60` : 'var(--shadow-md)'
                  }}
                >
                  {item.number ?? '—'}
                </div>
                <span className="result-meta">#{item.spin_number}</span>
              </div>
            );
          })
        ) : (
          <div className="empty-state">Aguardando resultados…</div>
        )}
      </div>
    </div>
  );
};

export default LiveResults;


