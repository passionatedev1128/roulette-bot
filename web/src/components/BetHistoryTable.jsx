import React, { useEffect } from 'react';

const formatNumber = (value) => (value !== undefined && value !== null
  ? new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 2,
    }).format(Number(value))
  : '—');

const resultLabels = {
  win: 'vitória',
  loss: 'derrota',
};

const formatTimestamp = (value, index) => {
  if (!value) {
    return '—';
  }
  const inputDate = new Date(value);
  const currentDate = new Date();
  // Use current date but preserve time from timestamp with sequential offset
  const adjustedDate = new Date(currentDate);
  adjustedDate.setHours(
    inputDate.getHours(),
    inputDate.getMinutes(),
    inputDate.getSeconds() + index * 5,
  );
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }  ).format(adjustedDate);
};

const BetHistoryTable = ({ history }) => {
  const hasContent = history?.bets?.length > 0;
  const entryCount = history?.bets?.length ?? 0;

  // Log when content appears or changes in betting history table
  useEffect(() => {
    if (hasContent) {
      console.log(
        `[Betting History Table] Table has content: ${entryCount} entry/entries. ` +
        `Latest: Spin #${history.bets[0]?.spin_number ?? 'N/A'}`
      );
    } else {
      console.log('[Betting History Table] Table is empty - no entries yet.');
    }
  }, [hasContent, entryCount, history?.bets]);

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Histórico de apostas</h2>
        <span className="panel-subtitle">
          {hasContent 
            ? `Últimas apostas resolvidas (${entryCount} ${entryCount === 1 ? 'entrada' : 'entradas'})`
            : 'Últimas apostas resolvidas'}
        </span>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Giro</th>
              <th>Tipo</th>
              <th>Valor</th>
              <th>Resultado</th>
              <th>P/L</th>
              <th>Saldo</th>
              <th>Horário</th>
            </tr>
          </thead>
          <tbody>
            {hasContent ? (
              history.bets.map((bet, index) => (
                <tr key={`${bet.spin_number}-${bet.timestamp}`}>
                  <td>#{bet.spin_number}</td>
                  <td>{bet.bet_type ?? '—'}</td>
                  <td>{formatNumber(bet.bet_amount)}</td>
                  <td className={`result-${bet.result}`}>{resultLabels[bet.result] ?? bet.result}</td>
                  <td style={{ 
                    color: bet.profit_loss >= 0 ? '#10b981' : '#ef4444',
                    fontWeight: 600
                  }}>
                    {bet.profit_loss >= 0 ? '+' : ''}{formatNumber(bet.profit_loss)}
                  </td>
                  <td>{formatNumber(bet.balance_after)}</td>
                  <td>{formatTimestamp(bet.timestamp, index)}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="empty-state">Nenhuma aposta registrada ainda.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default BetHistoryTable;


