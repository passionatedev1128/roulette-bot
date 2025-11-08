import React, { useEffect, useState } from 'react';

const modes = [
  'Maintenance Mode',
  'Full Auto Mode',
  'Manual Analysis Mode',
];

const ModeControls = ({ statusData, onStart, onStop, onModeChange, starting, stopping }) => {
  const [selectedMode, setSelectedMode] = useState(modes[1]);
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
        <h2>Bot Controls</h2>
        <span className="panel-subtitle">Start, pause, and select operating mode</span>
      </div>
      <div className="controls-grid">
        <label>
          <span>Mode</span>
          <select value={selectedMode} onChange={handleModeChange}>
            {modes.map((mode) => (
              <option key={mode} value={mode}>{mode}</option>
            ))}
          </select>
        </label>
        <label className="checkbox">
          <input type="checkbox" checked={testMode} onChange={(event) => setTestMode(event.target.checked)} />
          <span>Test Mode (simulation)</span>
        </label>
        <div className="control-buttons">
          <button type="button" className="primary" onClick={handleStart} disabled={isRunning || starting}>
            {starting ? 'Starting…' : 'Start Bot'}
          </button>
          <button type="button" className="secondary" onClick={onStop} disabled={!isRunning || stopping}>
            {stopping ? 'Stopping…' : 'Stop Bot'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModeControls;


