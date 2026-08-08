import React from 'react';
import { ExternalLink, Play } from 'lucide-react';
import { api } from '../api/client';

export const MockPortalSimPage: React.FC = () => {
  const handleTestAutoApply = async () => {
    try {
      const appRes = await api.createApplication(1, 'AUTO');
      await api.submitApplication(appRes.id);
      alert('Playwright browser automation successfully opened the portal, filled candidate details, attached custom PDF resume, and submitted application!');
    } catch (err: any) {
      alert(err.message || 'Automation test failed');
    }
  };

  return (
    <div>
      <div className="top-header">
        <div className="page-title">
          <h1>Interactive Mock ATS Application Portal Simulator</h1>
          <p>Demonstrate live browser automation with form input detection, custom answer typing, and PDF file attachment.</p>
        </div>
        <button className="btn-primary" onClick={handleTestAutoApply}>
          <Play size={16} /> Execute Playwright Auto-Fill Test
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3>Embedded Application Landing Page</h3>
          <a href="http://localhost:8000/api/v1/mock-portal/apply?job=demo-001" target="_blank" rel="noreferrer" className="btn-secondary" style={{ fontSize: '13px' }}>
            Open in New Window <ExternalLink size={14} />
          </a>
        </div>

        <iframe
          src="http://localhost:8000/api/v1/mock-portal/apply?job=demo-001"
          style={{ width: '100%', height: '540px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', background: '#0f172a' }}
          title="Mock ATS Form"
        />
      </div>
    </div>
  );
};
