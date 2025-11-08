import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  BarChart,
  Bar,
} from 'recharts';

const PerformanceCharts = ({ dailyStats, strategyStats, galeStats }) => {
  const dailyData = dailyStats?.stats ?? [];
  const galeData = galeStats?.stats ?? [];
  const strategyData = strategyStats?.stats ?? [];

  return (
    <div className="charts-grid">
      <div className="panel">
        <div className="panel-header">
          <h2>Daily Performance</h2>
          <span className="panel-subtitle">Profit/Loss by day</span>
        </div>
        {dailyData.length ? (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={[...dailyData].reverse()}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="profit_loss" stroke="#3b82f6" name="Profit/Loss" strokeWidth={2} />
              <Line type="monotone" dataKey="wins" stroke="#10b981" name="Wins" strokeWidth={2} />
              <Line type="monotone" dataKey="losses" stroke="#ef4444" name="Losses" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="empty-state">No statistics yet.</div>
        )}
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Gale Performance</h2>
          <span className="panel-subtitle">Win/Loss by gale step</span>
        </div>
        {galeData.length ? (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={galeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="gale_step" label={{ value: 'Gale Step', position: 'insideBottom', offset: -5 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="wins" fill="#10b981" name="Wins" />
              <Bar dataKey="losses" fill="#ef4444" name="Losses" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="empty-state">No gale data yet.</div>
        )}
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Strategy Breakdown</h2>
          <span className="panel-subtitle">Win rate by strategy</span>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Strategy</th>
                <th>Bets</th>
                <th>Wins</th>
                <th>Losses</th>
                <th>Win Rate</th>
                <th>P/L</th>
              </tr>
            </thead>
            <tbody>
              {strategyData.length ? (
                strategyData.map((row) => (
                  <tr key={row.strategy}>
                    <td>{row.strategy}</td>
                    <td>{row.bets}</td>
                    <td>{row.wins}</td>
                    <td>{row.losses}</td>
                    <td>{row.win_rate}%</td>
                    <td>{row.profit_loss.toFixed(2)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="empty-state">No strategy data yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PerformanceCharts;


