import React, { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import { api } from '../api/client';
import type { Application } from '../types';

export const ApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const data = await api.getApplications();
      setApplications(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleManualSubmit = async (appId: number) => {
    try {
      await api.submitApplication(appId);
      await fetchApplications();
      alert('Application submitted successfully via Playwright automation!');
    } catch (err: any) {
      alert(err.message || 'Submission failed');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUBMITTED':
        return <span className="badge-status badge-submitted">SUBMITTED</span>;
      case 'ACTION_REQUIRED':
        return <span className="badge-status badge-action">ACTION REQUIRED</span>;
      case 'FAILED':
        return <span className="badge-status badge-failed">FAILED</span>;
      default:
        return <span className="badge-status badge-ready">{status}</span>;
    }
  };

  return (
    <div>
      <div className="top-header">
        <div className="page-title">
          <h1>Applications Tracker</h1>
          <p>Track job submission status, view tailored resumes, and review AI generated answers.</p>
        </div>
      </div>

      <div className="glass-panel table-container">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Salary (LPA)</th>
              <th>Custom Resume</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {applications.map((app) => (
              <tr key={app.id}>
                <td>
                  <strong>{app.job?.company || 'Company'}</strong>
                </td>
                <td>{app.job?.title || 'Role'}</td>
                <td>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 700 }}>
                    ₹{app.job?.salary_min_lpa}–{app.job?.salary_max_lpa} LPA
                  </span>
                </td>
                <td>
                  {app.pdf_url ? (
                    <a href={`http://localhost:8000${app.pdf_url}`} target="_blank" rel="noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--accent-cyan)' }}>
                      <FileText size={14} /> Download PDF
                    </a>
                  ) : (
                    <span style={{ color: 'var(--text-muted)' }}>Generating...</span>
                  )}
                </td>
                <td>{getStatusBadge(app.status)}</td>
                <td>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => setSelectedApp(app)}>
                      Details
                    </button>
                    {app.status !== 'SUBMITTED' && (
                      <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => handleManualSubmit(app.id)}>
                        Submit Now
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Application Detail Modal */}
      {selectedApp && (
        <div className="modal-overlay" onClick={() => setSelectedApp(null)}>
          <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '16px' }}>Application Record Details</h2>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)', marginBottom: '16px' }}>
              <strong>AI Generated Application Question Answers:</strong>
              {Object.entries(selectedApp.answers_json || {}).map(([q, a], idx) => (
                <div key={idx} style={{ marginTop: '8px', fontSize: '13px' }}>
                  <div style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Q: {q}</div>
                  <div style={{ color: 'var(--text-secondary)' }}>A: {a}</div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn-secondary" onClick={() => setSelectedApp(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
