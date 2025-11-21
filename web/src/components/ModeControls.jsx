import React, { useEffect, useState } from 'react';

const modes = [
  { value: 'Maintenance Mode', label: 'Modo de manutenção' },
  { value: 'Full Auto Mode', label: 'Modo totalmente automático' },
  { value: 'Manual Analysis Mode', label: 'Modo de análise manual' },
];

const ModeControls = ({ statusData, onStart, onStop, onModeChange, starting, stopping }) => {
  const [selectedMode, setSelectedMode] = useState(modes[1].value);
  const [testMode, setTestMode] = useState(false);

  useEffect(() => {
    if (statusData?.mode) {
      setSelectedMode(statusData.mode);
    }
  }, [statusData?.mode]);

  const handleModeChange = (event) => {
    const mode = event.target.value;
    setSelectedMode(mode);
    onModeChange(mode);
  };

  const handleStart = () => {
    onStart({ mode: selectedMode, testMode });
  };

  const isRunning = statusData?.running;

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Controles do bot</h2>
        <span className="panel-subtitle">Inicie, pause e escolha o modo de operação</span>
      </div>
      <div className="controls-grid">
        <label>
          <select value={selectedMode} onChange={handleModeChange} disabled={isRunning || starting}>
            {modes.map((mode) => (
              <option key={mode.value} value={mode.value}>{mode.label}</option>
            ))}
          </select>
        </label>
        <label className="checkbox">
          <input 
            type="checkbox" 
            checked={testMode} 
            onChange={(event) => setTestMode(event.target.checked)}
            disabled={isRunning || starting}
          />
          <span>Modo de teste (simulação)</span>
        </label>
        <div className="control-buttons">
          <button type="button" className="primary" onClick={handleStart} disabled={isRunning || starting}>
            {starting ? 'Iniciando…' : 'Iniciar bot'}
          </button>
          <button type="button" className="secondary" onClick={onStop} disabled={!isRunning || stopping}>
            {stopping ? 'Parando…' : 'Parar bot'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModeControls;


