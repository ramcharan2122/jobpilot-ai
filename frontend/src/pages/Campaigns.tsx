import React, { useState, useEffect } from 'react';
import { Layers, Play } from 'lucide-react';
import { api } from '../api/client';
import type { Campaign } from '../types';

export const CampaignsPage: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [name, setName] = useState('Production 300 Apps/Day High-Volume Campaign');
  const [minLpa, setMinLpa] = useState(8.0);
  const [maxLpa, setMaxLpa] = useState(18.0);
  const [dailyLimit, setDailyLimit] = useState(300);
  const [autoApply, setAutoApply] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const data = await api.getCampaigns();
      setCampaigns(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    setRunning(true);
    try {
      await api.createCampaign({
        name,
        min_lpa: minLpa,
        max_lpa: maxLpa,
        target_roles: ['Software Engineer', 'Python Developer', 'Backend Developer', 'GenAI Engineer', 'AI Engineer'],
        locations: ['India', 'Remote', 'Bangalore', 'Hyderabad', 'Pune'],
        min_match_score: 75,
        daily_limit: dailyLimit,
        auto_apply: autoApply
      });
      await fetchCampaigns();
      alert(`Mass application campaign launched with high-volume capacity of ${dailyLimit} apps/day!`);
    } catch (err: any) {
      alert(err.message || 'Failed to create campaign');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <div className="top-header">
        <div className="page-title">
          <h1>High-Volume Mass Application Campaigns</h1>
          <p>Execute automated application worker queues applying up to 200–300 software engineering jobs per day.</p>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '28px', marginBottom: '32px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={20} style={{ color: 'var(--accent-cyan)' }} /> Launch High-Volume Campaign (Up to 300 Apps/Day)
        </h3>

        <form onSubmit={handleCreateCampaign}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '16px', marginBottom: '20px' }}>
            <div className="form-group">
              <label>Campaign Name</label>
              <input className="form-control" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Min Salary (LPA)</label>
              <input type="number" step="0.5" className="form-control" value={minLpa} onChange={(e) => setMinLpa(parseFloat(e.target.value))} />
            </div>
            <div className="form-group">
              <label>Max Salary (LPA)</label>
              <input type="number" step="0.5" className="form-control" value={maxLpa} onChange={(e) => setMaxLpa(parseFloat(e.target.value))} />
            </div>
            <div className="form-group">
              <label>Daily Volume Preset</label>
              <select className="form-control" value={dailyLimit} onChange={(e) => setDailyLimit(parseInt(e.target.value))}>
                <option value={50}>50 Applications/Day</option>
                <option value={100}>100 Applications/Day</option>
                <option value={200}>200 Applications/Day</option>
                <option value={300}>300 Applications/Day (MAX)</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '14px', cursor: 'pointer' }}>
              <input type="checkbox" checked={autoApply} onChange={(e) => setAutoApply(e.target.checked)} />
              <span>Enable Playwright Cluster Auto-Submission Agent</span>
            </label>
            <button type="submit" className="btn-primary" disabled={running}>
              <Play size={16} /> {running ? 'Processing High-Volume Queue...' : `Launch ${dailyLimit} Apps/Day Batch`}
            </button>
          </div>
        </form>
      </div>

      <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '16px' }}>Campaign History & Funnel Analytics</h3>

      <div className="glass-panel table-container">
        <table>
          <thead>
            <tr>
              <th>Campaign</th>
              <th>Status</th>
              <th>Discovered</th>
              <th>Eligible</th>
              <th>Applied</th>
              <th>Action Needed</th>
            </tr>
          </thead>
          <tbody>
            {campaigns.map((c) => (
              <tr key={c.id}>
                <td><strong>{c.name}</strong></td>
                <td><span className="badge-status badge-ready">{c.status}</span></td>
                <td>{c.total_discovered}</td>
                <td><span style={{ color: 'var(--accent-emerald)', fontWeight: 700 }}>{c.total_eligible}</span></td>
                <td><span style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>{c.total_applied}</span></td>
                <td><span style={{ color: 'var(--accent-amber)', fontWeight: 700 }}>{c.total_action_required}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
