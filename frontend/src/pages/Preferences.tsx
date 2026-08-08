import React, { useState, useEffect } from 'react';
import { Sliders, CheckCircle2, DollarSign } from 'lucide-react';
import { api } from '../api/client';
import type { UserSettings } from '../types';

export const PreferencesPage: React.FC = () => {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const data = await api.getSettings();
      setSettings(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      await api.updateSettings(settings);
      alert('Preferences and LPA settings saved!');
    } catch (err: any) {
      alert(err.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="top-header">
        <div className="page-title">
          <h1>LPA Salary & High-Volume Preferences</h1>
          <p>Configure strict LPA compensation thresholds, application automation mode, and daily volume (up to 300 apps/day).</p>
        </div>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          <CheckCircle2 size={18} /> {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <DollarSign size={20} style={{ color: 'var(--accent-emerald)' }} /> Salary & LPA Filter Controls
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div className="form-group">
            <label>Minimum Salary (INR LPA)</label>
            <input
              type="number"
              step="0.5"
              className="form-control"
              value={settings?.min_lpa || 8.0}
              onChange={(e) => setSettings({ ...settings!, min_lpa: parseFloat(e.target.value) })}
            />
          </div>
          <div className="form-group">
            <label>Maximum Target Salary (INR LPA)</label>
            <input
              type="number"
              step="0.5"
              className="form-control"
              value={settings?.max_lpa || 15.0}
              onChange={(e) => setSettings({ ...settings!, max_lpa: parseFloat(e.target.value) })}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', fontSize: '14px' }}>
            <input
              type="checkbox"
              checked={settings?.apply_undisclosed_salary || false}
              onChange={(e) => setSettings({ ...settings!, apply_undisclosed_salary: e.target.checked })}
            />
            <span>Apply to jobs with undisclosed salary</span>
          </label>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '28px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Sliders size={20} style={{ color: 'var(--accent-cyan)' }} /> Automation Mode & High-Volume Daily Limits
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '24px' }}>
          {['MANUAL', 'APPROVAL', 'AUTO'].map((m) => (
            <div
              key={m}
              onClick={() => setSettings({ ...settings!, application_mode: m as any, auto_apply_enabled: m === 'AUTO' })}
              style={{
                padding: '20px',
                borderRadius: 'var(--radius-md)',
                border: `2px solid ${settings?.application_mode === m ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
                background: settings?.application_mode === m ? 'rgba(56, 189, 248, 0.1)' : 'rgba(15, 23, 42, 0.4)',
                cursor: 'pointer'
              }}
            >
              <h4 style={{ fontWeight: 700, marginBottom: '6px' }}>{m} MODE</h4>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                {m === 'MANUAL' && 'Prepares applications & custom resumes. You submit manually.'}
                {m === 'APPROVAL' && 'Generates custom resume & answers. Requires user click before submission.'}
                {m === 'AUTO' && 'Playwright agent automatically fills forms & submits eligible jobs.'}
              </p>
            </div>
          ))}
        </div>

        <div className="form-group" style={{ maxWidth: '400px' }}>
          <label style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Daily Application Capacity Limit:</span>
            <strong style={{ color: 'var(--accent-cyan)' }}>{settings?.daily_application_limit || 200} Apps/Day</strong>
          </label>
          <input
            type="range"
            min="10"
            max="300"
            step="10"
            className="form-control"
            value={settings?.daily_application_limit || 200}
            onChange={(e) => setSettings({ ...settings!, daily_application_limit: parseInt(e.target.value) })}
          />
        </div>
      </div>
    </div>
  );
};
