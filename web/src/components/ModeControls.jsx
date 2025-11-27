import React, { useEffect, useState } from 'react';
import Dropdown from './Dropdown';

const modes = [
  { value: 'Maintenance Mode', label: 'Modo de manutenção' },
  { value: 'Full Auto Mode', label: 'Modo totalmente automático' },
  { value: 'Manual Analysis Mode', label: 'Modo de análise manual' },
];

const ModeControls = ({ statusData, onStart, onStop, onModeChange, starting, stopping, wsConnectionStatus, apiConnectionStatus }) => {
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
    if (onModeChange) {
      onModeChange(mode);
    }
  };

  const handleStart = () => {
    onStart({ mode: selectedMode, testMode });
  };

  const isRunning = statusData?.running;
  
  // Disable start button if websocket or API is not connected
  const isConnected = wsConnectionStatus === 'connected' && apiConnectionStatus === 'connected';
  const canStart = !isRunning && !starting && isConnected;

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Controles do bot</h2>
        <span className="panel-subtitle">Inicie, pause e escolha o modo de operação</span>
      </div>
      <div className="controls-grid">
        <label>
          <Dropdown
            value={selectedMode}
            onChange={handleModeChange}
            options={modes}
            disabled={isRunning || starting}
          />
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
          <button 
            type="button" 
            className="primary" 
            onClick={handleStart} 
            disabled={!canStart}
            title={!isConnected ? 'Aguardando conexão WebSocket e API REST...' : ''}
          >
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


