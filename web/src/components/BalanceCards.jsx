import React from 'react';

const formatCurrency = (value) => {
  if (value === undefined || value === null) {
    return '—';
  }
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 2,
  }).format(value);
};

const BalanceCards = ({ balance }) => {
  const profitLoss = balance?.profit_loss ?? 0;
  const todayProfitLoss = balance?.today_profit_loss ?? 0;
  
  const cards = [
    { 
      label: 'Saldo atual', 
      value: formatCurrency(balance?.current_balance),
      highlight: true
    },
    { 
      label: 'Saldo inicial', 
      value: formatCurrency(balance?.initial_balance) 
    },
    { 
      label: 'P/L total', 
      value: formatCurrency(profitLoss),
      className: profitLoss >= 0 ? 'positive' : 'negative'
    },
    { 
      label: 'P/L do dia', 
      value: formatCurrency(todayProfitLoss),
      className: todayProfitLoss >= 0 ? 'positive' : 'negative'
    },
    { 
      label: 'Apostas totais', 
      value: balance?.total_bets ?? 0 
    },
    { 
      label: 'Vitórias', 
      value: balance?.wins ?? 0,
      className: 'positive'
    },
    { 
      label: 'Derrotas', 
      value: balance?.losses ?? 0,
      className: 'negative'
    },
  ];

  return (
    <div className="cards-grid">
      {cards.map((card) => (
        <div 
          key={card.label} 
          className="card"
        >
          <span className="card-label">{card.label}</span>
          <span className={`card-value ${card.className || ''}`}>
            {card.value}
          </span>
        </div>
      ))}
    </div>
  );
};

export default BalanceCards;


