import React from 'react';

const formatCurrency = (value) => {
  if (value === undefined || value === null) {
    return '—';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value);
};

const BalanceCards = ({ balance }) => {
  const cards = [
    { label: 'Current Balance', value: formatCurrency(balance?.current_balance) },
    { label: 'Initial Balance', value: formatCurrency(balance?.initial_balance) },
    { label: 'Total P/L', value: formatCurrency(balance?.profit_loss) },
    { label: "Today's P/L", value: formatCurrency(balance?.today_profit_loss) },
    { label: 'Total Bets', value: balance?.total_bets ?? 0 },
    { label: 'Wins', value: balance?.wins ?? 0 },
    { label: 'Losses', value: balance?.losses ?? 0 },
  ];

  return (
    <div className="cards-grid">
      {cards.map((card) => (
        <div key={card.label} className="card">
          <span className="card-label">{card.label}</span>
          <span className="card-value">{card.value}</span>
        </div>
      ))}
    </div>
  );
};

export default BalanceCards;


