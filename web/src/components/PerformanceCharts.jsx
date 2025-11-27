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
    <>
      <div className="panel">
        <div className="panel-header">
          <h2>Desempenho diário</h2>
          <span className="panel-subtitle">Lucro/prejuízo por dia</span>
        </div>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={dailyData.length ? [...dailyData].reverse() : []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="profit_loss" 
              stroke="#6366f1" 
              name="Lucro/Prejuízo" 
              strokeWidth={3}
              dot={{ fill: '#6366f1', r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line 
              type="monotone" 
              dataKey="wins" 
              stroke="#10b981" 
              name="Vitórias" 
              strokeWidth={2}
              dot={{ fill: '#10b981', r: 3 }}
            />
            <Line 
              type="monotone" 
              dataKey="losses" 
              stroke="#ef4444" 
              name="Derrotas" 
              strokeWidth={2}
              dot={{ fill: '#ef4444', r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="panel gale-performance-panel">
        <div className="panel-header">
          <h2>Desempenho por gale</h2>
          <span className="panel-subtitle">Vitórias/derrotas por etapa do gale</span>
        </div>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={galeData.length ? galeData : []} margin={{ top: 20, right: 30, left: 30, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="gale_step" 
              label={{ value: '', position: 'insideBottom', offset: -5 }}
              tick={{ fontSize: 12 }}
            />
            <YAxis />
            <Tooltip />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Bar dataKey="wins" fill="#10b981" name="Vitórias" radius={[8, 8, 0, 0]} />
            <Bar dataKey="losses" fill="#ef4444" name="Derrotas" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default PerformanceCharts;


