import React, { useState, useEffect } from 'react';
import { FileText, RefreshCw, Loader2 } from 'lucide-react';
import { api, getDownloadUrl } from '../api/client';
import type { Application } from '../types';

export const ApplicationsPage: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [submittingId, setSubmittingId] = useState<number | null>(null);

  useEffect(() => {
    fetchApplications();
  }, []);

  // Polling mechanism to auto-refresh applications while resumes are generating
  useEffect(() => {
    const hasPending = applications.some(
      (app) => app.status === 'GENERATING_RESUME' || app.status === 'APPLYING' || app.status === 'READY' || !app.pdf_url
    );

    if (hasPending) {
      const interval = setInterval(() => {
        fetchApplications(true);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [applications]);

  const fetchApplications = async (isSilent: boolean = false) => {
    if (!isSilent) setLoading(true);
    try {
      const data = await api.getApplications();
      setApplications(data);
    } catch (err) {
      console.error("Failed to fetch applications:", err);
    } finally {
      if (!isSilent) setLoading(false);
    }
  };

  const handleManualSubmit = async (appId: number) => {
    setSubmittingId(appId);
    try {
      await api.submitApplication(appId);
      await fetchApplications();
    } catch (err: any) {
      alert(err.message || 'Submission failed');
    } finally {
      setSubmittingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUBMITTED':
        return <span className="badge-status badge-submitted">SUBMITTED</span>;
      case 'RESUME_READY':
        return <span className="badge-status" style={{ background: 'rgba(16, 185, 129, 0.2)', color: 'var(--accent-emerald)', border: '1px solid rgba(16, 185, 129, 0.4)' }}>RESUME READY</span>;
      case 'GENERATING_RESUME':
        return (
          <span className="badge-status" style={{ background: 'rgba(56, 189, 248, 0.2)', color: 'var(--accent-cyan)', border: '1px solid rgba(56, 189, 248, 0.4)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Loader2 size={12} className="spin" /> GENERATING RESUME
          </span>
        );
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
      <div className="top-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="page-title">
          <h1>Applications Tracker</h1>
          <p>Track job submission status, view tailored resumes, and review AI generated answers.</p>
        </div>
        <button className="btn-secondary" onClick={() => fetchApplications()} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          Refresh Status
        </button>
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
            {applications.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                  No job applications created yet. Go to <strong>Jobs Discovery</strong> and click <strong>1-Click Apply</strong>!
                </td>
              </tr>
            ) : (
              applications.map((app) => (
                <tr key={app.id}>
                  <td>
                    <strong>{app.job?.company || 'Company'}</strong>
                  </td>
                  <td>{app.job?.title || 'Role'}</td>
                  <td>
                    <span style={{ color: 'var(--accent-emerald)', fontWeight: 700 }}>
                      ₹{app.job?.salary_min_lpa || 10}–{app.job?.salary_max_lpa || 18} LPA
                    </span>
                  </td>
                  <td>
                    {app.pdf_url ? (
                      <a
                        href={getDownloadUrl(app.pdf_url)}
                        target="_blank"
                        rel="noreferrer"
                        className="btn-secondary"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 10px', fontSize: '12px', color: 'var(--accent-cyan)', background: 'rgba(56, 189, 248, 0.1)' }}
                      >
                        <FileText size={14} /> Download PDF
                      </a>
                    ) : (
                      <span style={{ color: 'var(--accent-cyan)', fontSize: '13px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                        <Loader2 size={14} className="spin" /> Generating...
                      </span>
                    )}
                  </td>
                  <td>{getStatusBadge(app.status)}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => setSelectedApp(app)}>
                        Details
                      </button>
                      {app.status !== 'SUBMITTED' && (
                        <button
                          className="btn-primary"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                          onClick={() => handleManualSubmit(app.id)}
                          disabled={submittingId === app.id}
                        >
                          {submittingId === app.id ? 'Submitting...' : 'Submit Now'}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Application Detail Modal */}
      {selectedApp && (
        <div className="modal-overlay" onClick={() => setSelectedApp(null)}>
          <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px', width: '90%' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '16px' }}>
              {selectedApp.job?.company} — {selectedApp.job?.title}
            </h2>

            {selectedApp.pdf_url && (
              <div style={{ marginBottom: '16px' }}>
                <a
                  href={getDownloadUrl(selectedApp.pdf_url)}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-primary"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
                >
                  <FileText size={16} /> Download Tailored PDF Resume
                </a>
              </div>
            )}

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)', marginBottom: '16px', maxHeight: '300px', overflowY: 'auto' }}>
              <strong style={{ color: 'var(--text-primary)', fontSize: '14px' }}>AI Generated Custom Answer Fields:</strong>
              {Object.keys(selectedApp.answers_json || {}).length === 0 ? (
                <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '8px' }}>Answers being generated by Gemini AI...</p>
              ) : (
                Object.entries(selectedApp.answers_json || {}).map(([q, a], idx) => (
                  <div key={idx} style={{ marginTop: '12px', fontSize: '13px', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '8px' }}>
                    <div style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Q: {q}</div>
                    <div style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>A: {a}</div>
                  </div>
                ))
              )}
            </div>

            {selectedApp.cover_letter && (
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)', marginBottom: '16px' }}>
                <strong style={{ color: 'var(--text-primary)', fontSize: '14px' }}>AI Generated Cover Letter:</strong>
                <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '8px', whiteSpace: 'pre-line', lineHeight: '1.5' }}>
                  {selectedApp.cover_letter}
                </p>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn-secondary" onClick={() => setSelectedApp(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
