import React, { useEffect, useMemo, useState } from 'react';

const deepClone = (value) => JSON.parse(JSON.stringify(value));

const updateNestedValue = (obj, path, newValue) => {
  const keys = path.split('.');
  const updated = deepClone(obj);
  let current = updated;
  for (let i = 0; i < keys.length - 1; i += 1) {
    const key = keys[i];
    if (!(key in current)) {
      current[key] = {};
    }
    current = current[key];
  }
  current[keys[keys.length - 1]] = newValue;
  return updated;
};

const ConfigForm = ({ configData, onSave, saving, presets, onSavePreset, onLoadPreset }) => {
  const [formValue, setFormValue] = useState(null);
  const [presetName, setPresetName] = useState('');
  const [selectedPreset, setSelectedPreset] = useState('');

  useEffect(() => {
    if (configData?.config) {
      setFormValue(deepClone(configData.config));
      setSelectedPreset('');
    }
  }, [configData]);

  const handleChange = (path) => (event) => {
    const value = event.target.type === 'number' ? Number(event.target.value) : event.target.value;
    setFormValue((prev) => (prev ? updateNestedValue(prev, path, value) : prev));
  };

  const handleToggle = (path) => (event) => {
    const value = event.target.checked;
    setFormValue((prev) => (prev ? updateNestedValue(prev, path, value) : prev));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (formValue) {
      onSave(formValue);
    }
  };

  const handlePresetLoad = (event) => {
    const value = event.target.value;
    if (!value) return;
    setSelectedPreset(value);
    onLoadPreset(value);
    setTimeout(() => setSelectedPreset(''), 0);
  };

  const handlePresetSave = () => {
    if (!presetName || !formValue) return;
    onSavePreset(presetName, formValue);
    setPresetName('');
  };

  const strategyOptions = useMemo(
    () => [
      { value: 'martingale', label: 'Martingale' },
      { value: 'fibonacci', label: 'Fibonacci' },
      { value: 'custom', label: 'Custom' },
    ],
    [],
  );

  if (!formValue) {
    return <div className="panel"><div className="empty-state">Loading configuration…</div></div>;
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Strategy Configuration</h2>
        <span className="panel-subtitle">Adjust bot parameters without editing JSON files</span>
      </div>
      <form className="config-form" onSubmit={handleSubmit}>
        <section>
          <h3>Strategy</h3>
          <div className="form-grid">
            <label>
              <span>Strategy Type</span>
              <select value={formValue.strategy?.type ?? ''} onChange={handleChange('strategy.type')}>
                {strategyOptions.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </label>
            <label>
              <span>Base Bet</span>
              <input type="number" min="0" step="0.1" value={formValue.strategy?.base_bet ?? 0} onChange={handleChange('strategy.base_bet')} />
            </label>
            <label>
              <span>Max Gales</span>
              <input type="number" min="0" step="1" value={formValue.strategy?.max_gales ?? 0} onChange={handleChange('strategy.max_gales')} />
            </label>
            <label>
              <span>Multiplier</span>
              <input type="number" min="1" step="0.1" value={formValue.strategy?.multiplier ?? 2} onChange={handleChange('strategy.multiplier')} />
            </label>
            <label>
              <span>Bet Color Pattern</span>
              <select value={formValue.strategy?.bet_color_pattern ?? ''} onChange={handleChange('strategy.bet_color_pattern')}>
                <option value="opposite">Opposite</option>
                <option value="same">Same</option>
                <option value="custom">Custom</option>
              </select>
            </label>
            <label className="checkbox">
              <input type="checkbox" checked={formValue.strategy?.zero_handling?.reset_on_zero ?? false} onChange={handleToggle('strategy.zero_handling.reset_on_zero')} />
              <span>Reset sequence on zero</span>
            </label>
          </div>
        </section>

        <section>
          <h3>Risk Management</h3>
          <div className="form-grid">
            <label>
              <span>Initial Balance</span>
              <input type="number" min="0" step="0.1" value={formValue.risk?.initial_balance ?? 0} onChange={handleChange('risk.initial_balance')} />
            </label>
            <label>
              <span>Stop Loss</span>
              <input type="number" min="0" step="0.1" value={formValue.risk?.stop_loss ?? 0} onChange={handleChange('risk.stop_loss')} />
            </label>
            <label>
              <span>Guarantee Fund %</span>
              <input type="number" min="0" max="100" step="1" value={formValue.risk?.guarantee_fund_percentage ?? 0} onChange={handleChange('risk.guarantee_fund_percentage')} />
            </label>
          </div>
        </section>

        <section>
          <h3>Maintenance</h3>
          <div className="form-grid">
            <label>
              <span>Maintenance Interval (seconds)</span>
              <input type="number" min="0" step="60" value={formValue.session?.maintenance_bet_interval ?? 0} onChange={handleChange('session.maintenance_bet_interval')} />
            </label>
            <label>
              <span>Minimum Bet Amount</span>
              <input type="number" min="0" step="0.1" value={formValue.session?.min_bet_amount ?? 0} onChange={handleChange('session.min_bet_amount')} />
            </label>
          </div>
        </section>

        <div className="form-actions">
          <button type="submit" className="primary" disabled={saving}>{saving ? 'Saving…' : 'Save Configuration'}</button>
          <div className="preset-actions">
            <input type="text" placeholder="Preset name" value={presetName} onChange={(event) => setPresetName(event.target.value)} />
            <button type="button" onClick={handlePresetSave} disabled={!presetName}>Save Preset</button>
            <select value={selectedPreset} onChange={handlePresetLoad}>
              <option value="" disabled>Load preset…</option>
              {(presets ?? []).map((preset) => (
                <option key={preset.slug} value={preset.slug}>{preset.name}</option>
              ))}
            </select>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ConfigForm;


