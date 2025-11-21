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

const ConfigForm = ({ configData, onSave, saving, presets, onSavePreset, onLoadPreset, isBotRunning }) => {
  const [formValue, setFormValue] = useState(null);
  const [presetName, setPresetName] = useState('');
  const [selectedPreset, setSelectedPreset] = useState('');

  useEffect(() => {
    console.log('ConfigForm received configData:', configData);
    if (configData?.config) {
      setFormValue(deepClone(configData.config));
      setSelectedPreset('');
    } else if (configData) {
      // Handle case where configData might be the config directly
      console.warn('ConfigData structure unexpected:', configData);
      if (typeof configData === 'object' && !configData.config) {
        // Maybe the response is just the config object
        setFormValue(deepClone(configData));
        setSelectedPreset('');
      }
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
      { value: 'custom', label: 'Personalizada' },
    ],
    [],
  );

  if (!formValue) {
    return <div className="panel"><div className="empty-state">Carregando configurações…</div></div>;
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Configuração da estratégia</h2>
        <span className="panel-subtitle">Ajuste os parâmetros do bot sem editar arquivos JSON</span>
      </div>
      <form className="config-form" onSubmit={handleSubmit} style={{ opacity: isBotRunning ? 0.6 : 1, pointerEvents: isBotRunning ? 'none' : 'auto' }}>
        <section>
          <h3>Estratégia</h3>
          <div className="form-grid">
            <label>
              <span>Tipo de estratégia</span>
              <select value={formValue.strategy?.type ?? ''} onChange={handleChange('strategy.type')}>
                {strategyOptions.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </label>
            <label>
              <span>Aposta base</span>
              <input type="number" min="0" step="0.1" value={formValue.strategy?.base_bet ?? 0} onChange={handleChange('strategy.base_bet')} />
            </label>
            <label>
              <span>Máximo de gales</span>
              <input type="number" min="0" step="1" value={formValue.strategy?.max_gales ?? 0} onChange={handleChange('strategy.max_gales')} />
            </label>
            <label>
              <span>Multiplicador</span>
              <input type="number" min="1" step="0.1" value={formValue.strategy?.multiplier ?? 2} onChange={handleChange('strategy.multiplier')} />
            </label>
            <label>
              <span>Padrão de cor das apostas</span>
              <select value={formValue.strategy?.bet_color_pattern ?? ''} onChange={handleChange('strategy.bet_color_pattern')}>
                <option value="opposite">Oposta</option>
                <option value="same">Igual</option>
                <option value="custom">Personalizada</option>
              </select>
            </label>
            <label className="checkbox">
              <input type="checkbox" checked={formValue.strategy?.zero_handling?.reset_on_zero ?? false} onChange={handleToggle('strategy.zero_handling.reset_on_zero')} />
              <span>Reiniciar sequência no zero</span>
            </label>
          </div>
        </section>

        <section>
          <h3>Gestão de risco</h3>
          <div className="form-grid">
            <label>
              <span>Saldo inicial</span>
              <input type="number" min="0" step="0.1" value={formValue.risk?.initial_balance ?? 0} onChange={handleChange('risk.initial_balance')} />
            </label>
            <label>
              <span>Stop loss</span>
              <input type="number" min="0" step="0.1" value={formValue.risk?.stop_loss ?? 0} onChange={handleChange('risk.stop_loss')} />
            </label>
            <label>
              <span>% do fundo garantidor</span>
              <input type="number" min="0" max="100" step="1" value={formValue.risk?.guarantee_fund_percentage ?? 0} onChange={handleChange('risk.guarantee_fund_percentage')} />
            </label>
          </div>
        </section>

        <section>
          <h3>Manutenção</h3>
          <div className="form-grid">
            <label>
              <span>Intervalo de manutenção (segundos)</span>
              <input type="number" min="0" step="60" value={formValue.session?.maintenance_bet_interval ?? 0} onChange={handleChange('session.maintenance_bet_interval')} />
            </label>
            <label>
              <span>Valor mínimo da aposta</span>
              <input type="number" min="0" step="0.1" value={formValue.session?.min_bet_amount ?? 0} onChange={handleChange('session.min_bet_amount')} />
            </label>
          </div>
        </section>

        <div className="form-actions">
          {isBotRunning && (
            <div style={{ 
              padding: '8px 12px', 
              background: '#fef3c7', 
              border: '1px solid #fbbf24', 
              borderRadius: '4px', 
              marginBottom: '12px',
              fontSize: '14px',
              color: '#92400e'
            }}>
              ⚠️ Bot está em execução. A configuração está desabilitada.
            </div>
          )}
          <button type="submit" className="primary" disabled={saving || isBotRunning}>{saving ? 'Salvando…' : 'Salvar configurações'}</button>
          <div className="preset-actions">
            <input type="text" placeholder="Nome do preset" value={presetName} onChange={(event) => setPresetName(event.target.value)} />
            <button type="button" onClick={handlePresetSave} disabled={!presetName}>Salvar preset</button>
            <select value={selectedPreset} onChange={handlePresetLoad}>
              <option value="" disabled>Carregar preset…</option>
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


